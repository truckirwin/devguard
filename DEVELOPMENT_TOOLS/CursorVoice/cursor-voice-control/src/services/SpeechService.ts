import * as vscode from 'vscode';
import { createClient, LiveTranscriptionEvents } from '@deepgram/sdk';
import { ConfigurationService } from './ConfigurationService';

export type SpeechServiceState = 'idle' | 'listening' | 'processing' | 'error';

export interface MicrophoneTestResult {
    success: boolean;
    message: string;
}

export class SpeechService {
    private deepgramClient: any;
    private connection: any;
    private state: SpeechServiceState = 'idle';
    private transcriptEmitter = new vscode.EventEmitter<string>();
    private stateChangeEmitter = new vscode.EventEmitter<SpeechServiceState>();
    private isInitialized = false;

    constructor(private configurationService: ConfigurationService) {}

    public readonly onTranscriptReceived = this.transcriptEmitter.event;
    public readonly onStateChange = this.stateChangeEmitter.event;

    async initialize(): Promise<void> {
        const apiKey = this.configurationService.getDeepgramApiKey();
        if (!apiKey) {
            throw new Error('Deepgram API key not configured');
        }

        try {
            this.deepgramClient = createClient(apiKey);
            this.isInitialized = true;
            console.log('Speech service initialized with Deepgram');
        } catch (error) {
            console.error('Failed to initialize speech service:', error);
            throw error;
        }
    }

    async startListening(): Promise<void> {
        if (!this.isInitialized) {
            await this.initialize();
        }

        try {
            this.setState('listening');

            // Configure Deepgram connection
            const options = {
                model: 'nova-2',
                language: this.configurationService.getLanguage(),
                smart_format: true,
                punctuate: true,
                interim_results: true,
                endpointing: 300,
                vad_events: true
            };

            this.connection = this.deepgramClient.listen.live(options);

            this.setupConnectionHandlers();

            // Start microphone capture
            await this.startMicrophoneCapture();

        } catch (error) {
            console.error('Failed to start listening:', error);
            this.setState('error');
            throw error;
        }
    }

    async stopListening(): Promise<void> {
        if (this.connection) {
            this.connection.finish();
            this.connection = null;
        }
        this.setState('idle');
    }

    private setupConnectionHandlers(): void {
        if (!this.connection) return;

        this.connection.addListener(LiveTranscriptionEvents.Open, () => {
            console.log('Deepgram connection opened');
            this.setState('listening');
        });

        this.connection.addListener(LiveTranscriptionEvents.Transcript, (data: any) => {
            const transcript = data.channel?.alternatives?.[0]?.transcript;
            if (transcript && transcript.trim().length > 0) {
                if (data.is_final) {
                    console.log('Final transcript:', transcript);
                    this.transcriptEmitter.fire(transcript);
                } else {
                    console.log('Interim transcript:', transcript);
                }
            }
        });

        this.connection.addListener(LiveTranscriptionEvents.Close, () => {
            console.log('Deepgram connection closed');
            this.setState('idle');
        });

        this.connection.addListener(LiveTranscriptionEvents.Error, (error: any) => {
            console.error('Deepgram connection error:', error);
            this.setState('error');
        });

        this.connection.addListener(LiveTranscriptionEvents.Metadata, (data: any) => {
            console.log('Deepgram metadata:', data);
        });
    }

    private async startMicrophoneCapture(): Promise<void> {
        try {
            // Request microphone permission and start capture
            const stream = await navigator.mediaDevices.getUserMedia({
                audio: {
                    channelCount: 1,
                    sampleRate: 16000,
                    sampleSize: 16,
                    echoCancellation: true,
                    noiseSuppression: true,
                    autoGainControl: true
                }
            });

            this.processMicrophoneStream(stream);

        } catch (error) {
            console.error('Failed to start microphone capture:', error);
            this.setState('error');
            throw new Error('Microphone access denied or unavailable');
        }
    }

    private processMicrophoneStream(stream: MediaStream): void {
        if (!this.connection) return;

        const audioContext = new (window.AudioContext || (window as any).webkitAudioContext)();
        const source = audioContext.createMediaStreamSource(stream);
        const processor = audioContext.createScriptProcessor(1024, 1, 1);

        source.connect(processor);
        processor.connect(audioContext.destination);

        processor.onaudioprocess = (e) => {
            if (!this.connection) return;

            const inputData = e.inputBuffer.getChannelData(0);
            
            // Convert Float32Array to 16-bit PCM
            const pcmData = new Int16Array(inputData.length);
            for (let i = 0; i < inputData.length; i++) {
                pcmData[i] = Math.max(-32768, Math.min(32767, inputData[i] * 32768));
            }

            // Send audio data to Deepgram
            if (this.connection.getReadyState() === 1) {
                this.connection.send(pcmData.buffer);
            }
        };

        // Store references for cleanup
        (this as any).audioStream = stream;
        (this as any).audioContext = audioContext;
        (this as any).audioProcessor = processor;
    }

    async testMicrophone(): Promise<MicrophoneTestResult> {
        try {
            // Test microphone access
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            
            // Test for a short duration
            const audioContext = new (window.AudioContext || (window as any).webkitAudioContext)();
            const source = audioContext.createMediaStreamSource(stream);
            const analyser = audioContext.createAnalyser();
            source.connect(analyser);

            const dataArray = new Uint8Array(analyser.frequencyBinCount);
            let hasAudio = false;

            return new Promise((resolve) => {
                const checkAudio = () => {
                    analyser.getByteFrequencyData(dataArray);
                    const average = dataArray.reduce((a, b) => a + b) / dataArray.length;
                    
                    if (average > 10) {
                        hasAudio = true;
                    }
                };

                const interval = setInterval(checkAudio, 100);

                setTimeout(() => {
                    clearInterval(interval);
                    stream.getTracks().forEach(track => track.stop());
                    audioContext.close();

                    if (hasAudio) {
                        resolve({
                            success: true,
                            message: 'Microphone is working and detecting audio'
                        });
                    } else {
                        resolve({
                            success: false,
                            message: 'Microphone accessible but no audio detected. Please check your microphone settings.'
                        });
                    }
                }, 3000);
            });

        } catch (error: any) {
            return {
                success: false,
                message: `Microphone test failed: ${error.message}`
            };
        }
    }

    updateConfiguration(): void {
        // Reinitialize with new configuration if needed
        if (this.isInitialized) {
            const newApiKey = this.configurationService.getDeepgramApiKey();
            if (newApiKey) {
                this.deepgramClient = createClient(newApiKey);
            }
        }
    }

    private setState(newState: SpeechServiceState): void {
        if (this.state !== newState) {
            this.state = newState;
            this.stateChangeEmitter.fire(newState);
        }
    }

    dispose(): void {
        this.stopListening();
        
        // Clean up audio resources
        if ((this as any).audioStream) {
            (this as any).audioStream.getTracks().forEach((track: MediaStreamTrack) => track.stop());
        }
        if ((this as any).audioContext) {
            (this as any).audioContext.close();
        }

        this.transcriptEmitter.dispose();
        this.stateChangeEmitter.dispose();
    }
}

// Browser compatibility shims
declare global {
    interface Window {
        AudioContext: typeof AudioContext;
        webkitAudioContext: typeof AudioContext;
    }
} 