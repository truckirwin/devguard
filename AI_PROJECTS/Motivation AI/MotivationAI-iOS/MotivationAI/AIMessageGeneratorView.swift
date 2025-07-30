import SwiftUI
import Foundation

struct AIMessageGeneratorView: View {
    // Slider states
    @State private var intensity: Double = 50
    @State private var languageClean: Double = 50
    @State private var humorStyle: Double = 50
    @State private var actionOrientation: Double = 50
    @State private var messageLength: Double = 50
    @State private var musicStyle: Double = 50
    @State private var visualStyle: Double = 50
    
    // Input and output states
    @State private var userInput: String = ""
    @State private var generatedMessage: String = ""
    @State private var isGenerating: Bool = false
    @State private var messageStyle: String = ""
    @State private var musicType: String = ""
    @State private var visualType: String = ""
    @State private var showError: Bool = false
    @State private var errorMessage: String = ""
    
    var body: some View {
        NavigationView {
            ScrollView {
                VStack(spacing: 20) {
                    // Header
                    VStack(spacing: 8) {
                        Image(systemName: "brain.head.profile")
                            .font(.system(size: 50))
                            .foregroundColor(.orange)
                        
                        Text("AI Message Generator")
                            .font(.title)
                            .fontWeight(.bold)
                        
                        Text("Customize your perfect motivational message")
                            .font(.subheadline)
                            .foregroundColor(.secondary)
                    }
                    .padding(.top)
                    
                    // User Input
                    VStack(alignment: .leading, spacing: 8) {
                        Text("What do you need motivation for?")
                            .font(.headline)
                        
                        TextField("e.g., waking up early, starting a workout routine...", text: $userInput, axis: .vertical)
                            .textFieldStyle(RoundedBorderTextFieldStyle())
                            .lineLimit(3...6)
                    }
                    .padding(.horizontal)
                    
                    // Slider Controls
                    VStack(spacing: 20) {
                        SliderRow(title: "Intensity", value: $intensity, 
                                leftLabel: "😌 Chill", rightLabel: "💪 Drill Sergeant")
                        
                        SliderRow(title: "Language Style", value: $languageClean,
                                leftLabel: "🤬 Raw", rightLabel: "😇 Clean")
                        
                        SliderRow(title: "Humor Level", value: $humorStyle,
                                leftLabel: "😐 Serious", rightLabel: "😂 Funny")
                        
                        SliderRow(title: "Approach", value: $actionOrientation,
                                leftLabel: "🧘 Mindful", rightLabel: "⚡ Action")
                        
                        SliderRow(title: "Message Length", value: $messageLength,
                                leftLabel: "💬 Quote", rightLabel: "📜 Speech")
                        
                        SliderRow(title: "Music Style", value: $musicStyle,
                                leftLabel: "🎵 Chill", rightLabel: "🎸 Rock")
                        
                        SliderRow(title: "Visual Style", value: $visualStyle,
                                leftLabel: "🖼️ Still", rightLabel: "🎬 Video")
                    }
                    .padding(.horizontal)
                    
                    // Generate Button
                    Button(action: generateMessage) {
                        HStack {
                            if isGenerating {
                                ProgressView()
                                    .progressViewStyle(CircularProgressViewStyle(tint: .white))
                                    .scaleEffect(0.8)
                                Text("Generating...")
                            } else {
                                Image(systemName: "sparkles")
                                Text("Generate My Message")
                            }
                        }
                        .frame(maxWidth: .infinity)
                        .padding()
                        .background(userInput.isEmpty ? Color.gray : Color.orange)
                        .foregroundColor(.white)
                        .cornerRadius(10)
                        .font(.headline)
                    }
                    .disabled(userInput.isEmpty || isGenerating)
                    .padding(.horizontal)
                    
                    // Generated Message Display
                    if !generatedMessage.isEmpty {
                        VStack(alignment: .leading, spacing: 12) {
                            Text("Your Personalized Message")
                                .font(.headline)
                                .padding(.horizontal)
                            
                            VStack(spacing: 12) {
                                // Message Card
                                Text(generatedMessage)
                                    .padding()
                                    .background(Color(.systemGray6))
                                    .cornerRadius(12)
                                    .font(.body)
                                    .lineSpacing(4)
                                
                                // Metadata
                                HStack {
                                    VStack {
                                        Text("Style")
                                            .font(.caption)
                                            .foregroundColor(.secondary)
                                        Text(messageStyle.replacingOccurrences(of: "_", with: " ").capitalized)
                                            .font(.caption2)
                                            .fontWeight(.semibold)
                                    }
                                    
                                    Spacer()
                                    
                                    VStack {
                                        Text("Music")
                                            .font(.caption)
                                            .foregroundColor(.secondary)
                                        Text(musicType.replacingOccurrences(of: "_", with: " ").capitalized)
                                            .font(.caption2)
                                            .fontWeight(.semibold)
                                    }
                                    
                                    Spacer()
                                    
                                    VStack {
                                        Text("Visual")
                                            .font(.caption)
                                            .foregroundColor(.secondary)
                                        Text(visualType.replacingOccurrences(of: "_", with: " ").capitalized)
                                            .font(.caption2)
                                            .fontWeight(.semibold)
                                    }
                                }
                                .padding(.horizontal, 8)
                            }
                            .padding(.horizontal)
                        }
                    }
                    
                    Spacer(minLength: 20)
                }
            }
            .navigationBarHidden(true)
        }
        .alert("Error", isPresented: $showError) {
            Button("OK") { }
        } message: {
            Text(errorMessage)
        }
    }
    
    private func generateMessage() {
        guard !userInput.isEmpty else { return }
        
        isGenerating = true
        
        let preferences = [
            "user_input": userInput,
            "intensity": Int(intensity),
            "language_clean": Int(languageClean),
            "humor_style": Int(humorStyle),
            "action_orientation": Int(actionOrientation),
            "message_length": Int(messageLength),
            "music_style": Int(musicStyle),
            "visual_style": Int(visualStyle)
        ] as [String : Any]
        
        AIMessageService.shared.generateMessage(preferences: preferences) { result in
            DispatchQueue.main.async {
                isGenerating = false
                
                switch result {
                case .success(let response):
                    generatedMessage = response.messageText
                    messageStyle = response.style
                    musicType = response.musicStyle
                    visualType = response.visualStyle
                    
                case .failure(let error):
                    errorMessage = error.localizedDescription
                    showError = true
                }
            }
        }
    }
}

// MARK: - Supporting Views

struct SliderRow: View {
    let title: String
    @Binding var value: Double
    let leftLabel: String
    let rightLabel: String
    
    var body: some View {
        VStack(spacing: 8) {
            HStack {
                Text(title)
                    .font(.subheadline)
                    .fontWeight(.medium)
                Spacer()
                Text("\(Int(value))")
                    .font(.subheadline)
                    .foregroundColor(.orange)
                    .fontWeight(.semibold)
            }
            
            HStack {
                Text(leftLabel)
                    .font(.caption)
                    .foregroundColor(.secondary)
                Spacer()
                Text(rightLabel)
                    .font(.caption)
                    .foregroundColor(.secondary)
            }
            
            Slider(value: $value, in: 0...100)
                .accentColor(.orange)
        }
    }
}

// MARK: - Preview
struct AIMessageGeneratorView_Previews: PreviewProvider {
    static var previews: some View {
        AIMessageGeneratorView()
    }
} 