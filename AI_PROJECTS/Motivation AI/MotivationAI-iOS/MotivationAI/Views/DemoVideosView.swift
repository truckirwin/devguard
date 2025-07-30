import SwiftUI

struct DemoVideosView: View {
    @EnvironmentObject var appViewModel: AppViewModel
    @EnvironmentObject var profileManager: ProfileManager
    
    var body: some View {
        NavigationView {
            ScrollView {
                VStack(spacing: 24) {
                    // Header Section
                    VStack(spacing: 12) {
                        HStack {
                            Image(systemName: "bolt.circle.fill")
                                .font(.title)
                                .foregroundColor(.orange)
                            
                            Text("Let's Go!")
                                .font(.largeTitle)
                                .fontWeight(.bold)
                            
                            Spacer()
                        }
                        
                        HStack {
                            VStack(alignment: .leading, spacing: 4) {
                                Text("Rise & Grind Motivation")
                                    .font(.title2)
                                    .fontWeight(.semibold)
                                
                                Text("Powerful messages to fuel your job search")
                                    .font(.subheadline)
                                    .foregroundColor(.secondary)
                            }
                            Spacer()
                        }
                    }
                    .padding(.top)
                    
                    // Demo Videos Grid
                    LazyVGrid(columns: [
                        GridItem(.flexible()),
                        GridItem(.flexible())
                    ], spacing: 16) {
                        ForEach(DemoVideoScripts.allDemoScripts, id: \.id) { message in
                            DemoVideoCard(message: message) {
                                // Show the animated text message
                                print("🎯 DEBUG: Demo card tapped for: \(message.title)")
                                appViewModel.showAnimatedTextMessage(message)
                            }
                        }
                    }
                    .padding(.horizontal)
                    
                    // Quick Actions
                    VStack(alignment: .leading, spacing: 16) {
                        HStack {
                            Image(systemName: "flame.fill")
                                .foregroundColor(.red)
                            Text("Quick Actions")
                                .font(.headline)
                            Spacer()
                        }
                        
                        Button("🎬 Play Random Demo") {
                            let randomMessage = DemoVideoScripts.getRandomScript()
                            appViewModel.showAnimatedTextMessage(randomMessage)
                        }
                        .padding()
                        .frame(maxWidth: .infinity)
                        .background(
                            LinearGradient(
                                gradient: Gradient(colors: [Color.purple, Color.pink]),
                                startPoint: .leading,
                                endPoint: .trailing
                            )
                        )
                        .foregroundColor(.white)
                        .cornerRadius(12)
                        
                        Button("⚡ Perfect Timing") {
                            // Get message for current time of day
                            let hour = Calendar.current.component(.hour, from: Date())
                            var timeBasedMessages: [MotivationalMessage] = []
                            
                            switch hour {
                            case 6..<11:
                                timeBasedMessages = DemoVideoScripts.getMorningDemos()
                            case 11..<14:
                                timeBasedMessages = DemoVideoScripts.getMiddayDemos()
                            case 14..<18:
                                timeBasedMessages = DemoVideoScripts.getAfternoonDemos()
                            case 18..<22:
                                timeBasedMessages = DemoVideoScripts.getEveningDemos()
                            default:
                                timeBasedMessages = DemoVideoScripts.allDemoScripts
                            }
                            
                            if let message = timeBasedMessages.randomElement() {
                                appViewModel.showAnimatedTextMessage(message)
                            } else {
                                let randomMessage = DemoVideoScripts.getRandomScript()
                                appViewModel.showAnimatedTextMessage(randomMessage)
                            }
                        }
                        .padding()
                        .frame(maxWidth: .infinity)
                        .background(
                            LinearGradient(
                                gradient: Gradient(colors: [Color.blue, Color.cyan]),
                                startPoint: .leading,
                                endPoint: .trailing
                            )
                        )
                        .foregroundColor(.white)
                        .cornerRadius(12)
                    }
                    .padding(.horizontal)
                    
                    Spacer(minLength: 100)
                }
            }
            .navigationBarHidden(true)
        }
    }
}

struct DemoVideoCard: View {
    let message: MotivationalMessage
    let action: () -> Void
    
    var body: some View {
        Button(action: action) {
            VStack(alignment: .leading, spacing: 12) {
                HStack {
                    VStack(alignment: .leading, spacing: 2) {
                        Text(message.title)
                            .font(.subheadline)
                            .fontWeight(.bold)
                            .foregroundColor(!(message.backgroundImageName?.isEmpty ?? true) ? .white : .primary)
                            .lineLimit(2)
                        
                        Text(message.category.rawValue)
                            .font(.caption)
                            .foregroundColor(!(message.backgroundImageName?.isEmpty ?? true) ? .white.opacity(0.8) : .secondary)
                    }
                    
                    Spacer()
                    
                    Image(systemName: "play.circle.fill")
                        .font(.title)
                        .foregroundColor(colorForCategory(message.category))
                }
                
                Text(message.shortContent)
                    .font(.caption)
                    .foregroundColor(!(message.backgroundImageName?.isEmpty ?? true) ? .white.opacity(0.9) : .secondary)
                    .lineLimit(3)
                
                Spacer()
                
                HStack {
                    Text("~\(message.duration)s")
                        .font(.caption2)
                        .foregroundColor(!(message.backgroundImageName?.isEmpty ?? true) ? .white.opacity(0.8) : .secondary)
                    
                    Spacer()
                    
                    HStack(spacing: 2) {
                        Image(systemName: toneIcon(message.tone))
                            .font(.caption2)
                            .foregroundColor(!(message.backgroundImageName?.isEmpty ?? true) ? .white : colorForCategory(message.category))
                        
                        Text(message.tone.rawValue)
                            .font(.caption2)
                            .foregroundColor(!(message.backgroundImageName?.isEmpty ?? true) ? .white : colorForCategory(message.category))
                    }
                }
            }
            .padding()
            .frame(height: 140)
            .background(
                ZStack {
                    if !(message.backgroundImageName?.isEmpty ?? true) {
                        // Background image
                        Image(message.backgroundImageName ?? "")
                            .resizable()
                            .aspectRatio(contentMode: .fill)
                            .clipped()
                        
                        // Semi-transparent overlay for text readability
                        Color.black.opacity(0.4)
                    } else {
                        // Default background
                        Color(UIColor.systemBackground)
                    }
                }
            )
            .cornerRadius(12)
            .shadow(color: .black.opacity(0.1), radius: 2, x: 0, y: 1)
            .overlay(
                RoundedRectangle(cornerRadius: 12)
                    .stroke(colorForCategory(message.category).opacity(0.3), lineWidth: 1)
            )
        }
        .buttonStyle(PlainButtonStyle())
    }
    
    private func colorForCategory(_ category: MessageCategory) -> Color {
        switch category {
        case .morningWakeUp: return .orange
        case .midDayCheckIn: return .blue
        case .eveningWindDown: return .purple
        case .linkedInFocus: return .blue
        case .rejectionRecovery: return .green
        case .interviewPrep: return .indigo
        case .networkBuilding: return .cyan
        case .fridayMotivation: return .yellow
        case .mondayEnergy: return .red
        case .actionOriented: return .orange
        default: return .primary
        }
    }
    
    private func toneIcon(_ tone: MessageTone) -> String {
        switch tone {
        case .energetic: return "bolt.fill"
        case .toughLove: return "flame.fill"
        case .compassionate: return "heart.fill"
        case .professional: return "briefcase.fill"
        case .actionFocused: return "target"
        case .inspiring: return "star.fill"
        case .playful: return "gamecontroller.fill"
        }
    }

}

#Preview {
    DemoVideosView()
        .environmentObject(AppViewModel())
        .environmentObject(ProfileManager())
} 