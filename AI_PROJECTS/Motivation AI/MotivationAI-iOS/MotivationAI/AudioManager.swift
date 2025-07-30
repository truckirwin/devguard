import Foundation
import AVFoundation

// MARK: - Audio Timing Models
struct AudioTimestamp {
    let startTime: TimeInterval
    let endTime: TimeInterval
    let text: String
}

struct MessageAudioData {
    let messageId: String
    let audioFileName: String
    let timestamps: [AudioTimestamp]
}

// MARK: - AudioManager
class AudioManager: NSObject, ObservableObject {
    
    // MARK: - Properties
    private var audioPlayer: AVAudioPlayer?
    private var displayTimer: Timer?
    private var currentAudioData: MessageAudioData?
    
    @Published var isPlaying = false
    @Published var currentTimestamp: AudioTimestamp?
    @Published var currentTime: TimeInterval = 0
    
    // MARK: - Audio Data Configuration
    private let audioDataMap: [String: MessageAudioData] = [
        "rise_up_job_hunter": MessageAudioData(
            messageId: "rise_up_job_hunter",
            audioFileName: "GetTheFckPutofBed",
            timestamps: [
                AudioTimestamp(startTime: 0.859, endTime: 2.679, text: "Get the fuck out of bed, get showered and"),
                AudioTimestamp(startTime: 2.7, endTime: 4.859, text: "grab a goddamn cup of coffee. Fuel for"),
                AudioTimestamp(startTime: 4.92, endTime: 7.039, text: "today's fire. That company that ghosted"),
                AudioTimestamp(startTime: 7.079, endTime: 9.18, text: "you? Their fucking loss. You're not"),
                AudioTimestamp(startTime: 9.26, endTime: 11.46, text: "rebuilding, you're upgrading. Your task"),
                AudioTimestamp(startTime: 11.5, endTime: 13.18, text: "list isn't just a to-do list. It's your"),
                AudioTimestamp(startTime: 13.259, endTime: 15.239, text: "battle plan. Every application is a"),
                AudioTimestamp(startTime: 15.299, endTime: 17.139, text: "missile aimed at mediocrity. Every"),
                AudioTimestamp(startTime: 17.219, endTime: 18.679, text: "interview prep session is training for"),
                AudioTimestamp(startTime: 18.719, endTime: 20.92, text: "war. The job market thinks it's tough."),
                AudioTimestamp(startTime: 21.159, endTime: 23.299, text: "Wait until it meets you. You've survived"),
                AudioTimestamp(startTime: 23.299, endTime: 24.739, text: "being unemployed. That makes you"),
                AudioTimestamp(startTime: 24.76, endTime: 26.92, text: "resilient. You faced uncertainty."),
                AudioTimestamp(startTime: 27.819, endTime: 29.12, text: "That makes you adaptable."),
                AudioTimestamp(startTime: 30.099, endTime: 31.619, text: "Those tasks won't complete themselves"),
                AudioTimestamp(startTime: 31.639, endTime: 33.799, text: "while you're contemplating life. Get up"),
                AudioTimestamp(startTime: 33.819, endTime: 35.579, text: "and show this day what a determined job"),
                AudioTimestamp(startTime: 35.639, endTime: 37.979, text: "seeker looks like. Your opportunity is"),
                AudioTimestamp(startTime: 38.04, endTime: 40.159, text: "waiting. Now go fucking get it.")
            ]
        ),
        "hunt_mode_activated": MessageAudioData(
            messageId: "hunt_mode_activated",
            audioFileName: "YouHeardMeRight",
            timestamps: [
                AudioTimestamp(startTime: 0.099, endTime: 1.819, text: "Yeah, you heard me right. That last job"),
                AudioTimestamp(startTime: 1.819, endTime: 4.099, text: "didn't work out. So fucking what? That"),
                AudioTimestamp(startTime: 4.139, endTime: 5.699, text: "wasn't your destination. That was just a"),
                AudioTimestamp(startTime: 5.699, endTime: 7.899, text: "pit stop on your way to greatness. Today's"),
                AudioTimestamp(startTime: 7.96, endTime: 9.92, text: "task list is sitting there waiting for"),
                AudioTimestamp(startTime: 9.96, endTime: 12.3, text: "you like a loyal dog. Those applications"),
                AudioTimestamp(startTime: 12.3, endTime: 14.659, text: "won't submit themselves. Those networking"),
                AudioTimestamp(startTime: 14.679, endTime: 18.619, text: "calls won't make themselves. That LinkedIn"),
                AudioTimestamp(startTime: 18.639, endTime: 21.379, text: "profile won't optimize itself. You think"),
                AudioTimestamp(startTime: 21.399, endTime: 23.0, text: "successful people got where they are by"),
                AudioTimestamp(startTime: 23.059, endTime: 26.34, text: "hitting snooze? Hell no. They got up every"),
                AudioTimestamp(startTime: 26.459, endTime: 27.919, text: "morning knowing that their future"),
                AudioTimestamp(startTime: 27.92, endTime: 31.119, text: "depended on their hustle. Your dream job"),
                AudioTimestamp(startTime: 31.119, endTime: 32.84, text: "is out there right now wondering where the"),
                AudioTimestamp(startTime: 32.86, endTime: 35.04, text: "hell you are. Stop keeping it waiting."),
                AudioTimestamp(startTime: 35.279, endTime: 37.679, text: "Get up, get caffeinated, and get hunting."),
                AudioTimestamp(startTime: 37.919, endTime: 39.659, text: "Today's the day you turn rejection into"),
                AudioTimestamp(startTime: 39.659, endTime: 41.739, text: "redirection. Let's go.")
            ]
        ),
        "momentum_machine": MessageAudioData(
            messageId: "momentum_machine",
            audioFileName: "FrpomTheAshes",
            timestamps: [
                AudioTimestamp(startTime: 0.14, endTime: 3.319, text: "From the ashes of that old job, you're"),
                AudioTimestamp(startTime: 3.319, endTime: 6.019, text: "building something bigger, better, more"),
                AudioTimestamp(startTime: 6.119, endTime: 9.139, text: "badass. This isn't a setback, this is your"),
                AudioTimestamp(startTime: 9.179, endTime: 12.159, text: "comeback. That task list is your roadmap"),
                AudioTimestamp(startTime: 12.219, endTime: 15.46, text: "to victory. Every item checked off is"),
                AudioTimestamp(startTime: 15.5, endTime: 17.799, text: "another step closer to your new empire."),
                AudioTimestamp(startTime: 18.239, endTime: 20.639, text: "Every networking message sent is building"),
                AudioTimestamp(startTime: 20.68, endTime: 23.0, text: "your army of supporters. You think"),
                AudioTimestamp(startTime: 23.059, endTime: 25.679, text: "rebuilding is weakness? Fuck that."),
                AudioTimestamp(startTime: 26.059, endTime: 28.399, text: "Rebuilding is evolution. It's taking"),
                AudioTimestamp(startTime: 28.42, endTime: 30.019, text: "everything you learned and making it"),
                AudioTimestamp(startTime: 30.079, endTime: 33.52, text: "stronger, smarter, more strategic. Today's"),
                AudioTimestamp(startTime: 33.52, endTime: 35.579, text: "not about finding any job, it's about"),
                AudioTimestamp(startTime: 35.7, endTime: 38.279, text: "finding your job. The one that makes you"),
                AudioTimestamp(startTime: 38.34, endTime: 41.079, text: "jump out of bed excited to dominate. Stop"),
                AudioTimestamp(startTime: 41.159, endTime: 42.819, text: "analyzing and start attacking."),
                AudioTimestamp(startTime: 43.439, endTime: 44.799, text: "Let's go.")
            ]
        )
    ]
    
    // MARK: - Public Methods
    func playAudioForMessage(_ messageId: String) {
        guard let audioData = audioDataMap[messageId] else {
            print("⚠️ No audio data found for message: \(messageId)")
            return
        }
        
        setupAudioSession()
        loadAudioFile(audioData)
    }
    
    func stopAudio() {
        audioPlayer?.stop()
        displayTimer?.invalidate()
        displayTimer = nil
        isPlaying = false
        currentTimestamp = nil
        currentTime = 0
    }
    
    func pauseAudio() {
        audioPlayer?.pause()
        displayTimer?.invalidate()
        isPlaying = false
    }
    
    func resumeAudio() {
        audioPlayer?.play()
        startDisplayTimer()
        isPlaying = true
    }
    
    // MARK: - Private Methods
    private func setupAudioSession() {
        do {
            try AVAudioSession.sharedInstance().setCategory(.playback, mode: .default)
            try AVAudioSession.sharedInstance().setActive(true)
        } catch {
            print("⚠️ Failed to setup audio session: \(error)")
        }
    }
    
    private func loadAudioFile(_ audioData: MessageAudioData) {
        guard let audioPath = Bundle.main.path(forResource: audioData.audioFileName, ofType: "mp3") else {
            print("⚠️ Could not find audio file: \(audioData.audioFileName).mp3")
            return
        }
        
        let audioUrl = URL(fileURLWithPath: audioPath)
        
        do {
            audioPlayer = try AVAudioPlayer(contentsOf: audioUrl)
            audioPlayer?.delegate = self
            audioPlayer?.prepareToPlay()
            
            currentAudioData = audioData
            
            audioPlayer?.play()
            startDisplayTimer()
            isPlaying = true
            
            print("✅ Started playing: \(audioData.audioFileName).mp3")
            
        } catch {
            print("⚠️ Error creating audio player: \(error)")
        }
    }
    
    private func startDisplayTimer() {
        displayTimer?.invalidate()
        displayTimer = Timer.scheduledTimer(withTimeInterval: 0.1, repeats: true) { [weak self] _ in
            self?.updateCurrentTimestamp()
        }
    }
    
    private func updateCurrentTimestamp() {
        guard let player = audioPlayer,
              let audioData = currentAudioData else { return }
        
        currentTime = player.currentTime
        
        // Find the current timestamp based on audio position
        let newTimestamp = audioData.timestamps.first { timestamp in
            currentTime >= timestamp.startTime && currentTime < timestamp.endTime
        }
        
        // Only update if timestamp changed
        if newTimestamp?.text != currentTimestamp?.text {
            currentTimestamp = newTimestamp
        }
    }
    
    // MARK: - Public Utility Methods
    func hasAudioForMessage(_ messageId: String) -> Bool {
        return audioDataMap[messageId] != nil
    }
    
    func getAudioDuration(for messageId: String) -> TimeInterval? {
        guard let audioData = audioDataMap[messageId],
              let audioPath = Bundle.main.path(forResource: audioData.audioFileName, ofType: "mp3") else {
            return nil
        }
        
        let audioUrl = URL(fileURLWithPath: audioPath)
        
        do {
            let tempPlayer = try AVAudioPlayer(contentsOf: audioUrl)
            return tempPlayer.duration
        } catch {
            print("⚠️ Error getting audio duration: \(error)")
            return nil
        }
    }
}

// MARK: - AVAudioPlayerDelegate
extension AudioManager: AVAudioPlayerDelegate {
    func audioPlayerDidFinishPlaying(_ player: AVAudioPlayer, successfully flag: Bool) {
        displayTimer?.invalidate()
        displayTimer = nil
        isPlaying = false
        currentTimestamp = nil
        currentTime = 0
        
        print("✅ Audio playback finished")
    }
    
    func audioPlayerDecodeErrorDidOccur(_ player: AVAudioPlayer, error: Error?) {
        print("⚠️ Audio decode error: \(error?.localizedDescription ?? "Unknown")")
        stopAudio()
    }
} 