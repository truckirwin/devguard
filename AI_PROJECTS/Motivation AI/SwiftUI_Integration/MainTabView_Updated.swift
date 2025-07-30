import SwiftUI

// Updated MainTabView to include AI Message Generator
struct MainTabView: View {
    @State private var selectedTab = 0
    
    var body: some View {
        TabView(selection: $selectedTab) {
            // Existing Home Tab
            DashboardView()
                .tabItem {
                    VStack {
                        Image(systemName: "house.fill")
                        Text("Home")
                    }
                }
                .tag(0)
            
            // Existing Demo Videos Tab
            DemoVideosView()
                .tabItem {
                    VStack {
                        Image(systemName: "bolt.circle.fill")
                        Text("Let's Go!")
                    }
                }
                .tag(1)
            
            // NEW: AI Generator Tab
            AIMessageGeneratorView()
                .tabItem {
                    VStack {
                        Image(systemName: "brain.head.profile")
                        Text("AI Create")
                    }
                }
                .tag(2)
            
            // Existing Tasks Tab
            TasksView()
                .tabItem {
                    VStack {
                        Image(systemName: "list.bullet")
                        Text("Tasks")
                    }
                }
                .tag(3)
            
            // Existing Learn Tab
            LearnView()
                .tabItem {
                    VStack {
                        Image(systemName: "book.fill")
                        Text("Learn")
                    }
                }
                .tag(4)
            
            // Existing Profile Tab
            ProfileView()
                .tabItem {
                    VStack {
                        Image(systemName: "person.fill")
                        Text("Profile")
                    }
                }
                .tag(5)
        }
        .accentColor(.orange) // Match your app's accent color
    }
}

// Alternative: Replace one of the existing demo video cards with AI generation
struct EnhancedDemoVideosView: View {
    @State private var showAIGenerator = false
    
    var body: some View {
        NavigationView {
            ScrollView {
                LazyVGrid(columns: [
                    GridItem(.flexible()),
                    GridItem(.flexible())
                ], spacing: 16) {
                    
                    // Existing demo video cards
                    ForEach(demoVideoItems) { item in
                        DemoVideoCard(item: item)
                    }
                    
                    // NEW: AI Generator Card
                    AIGeneratorCard {
                        showAIGenerator = true
                    }
                }
                .padding()
            }
            .navigationTitle("Rise & Grind Motivation")
        }
        .sheet(isPresented: $showAIGenerator) {
            AIMessageGeneratorView()
        }
    }
}

// Custom AI Generator Card to match existing design
struct AIGeneratorCard: View {
    let action: () -> Void
    
    var body: some View {
        Button(action: action) {
            VStack(spacing: 12) {
                // Icon
                ZStack {
                    Circle()
                        .fill(LinearGradient(
                            colors: [.orange, .red],
                            startPoint: .topLeading,
                            endPoint: .bottomTrailing
                        ))
                        .frame(width: 60, height: 60)
                    
                    Image(systemName: "brain.head.profile")
                        .font(.system(size: 30))
                        .foregroundColor(.white)
                }
                
                // Title
                Text("AI Custom")
                    .font(.headline)
                    .fontWeight(.bold)
                    .foregroundColor(.white)
                
                // Subtitle
                Text("Create Your Message")
                    .font(.caption)
                    .foregroundColor(.white.opacity(0.8))
                    .multilineTextAlignment(.center)
                
                // Message preview
                Text("PERSONALIZED MOTIVATION\nPOWERED BY AI")
                    .font(.caption2)
                    .fontWeight(.medium)
                    .foregroundColor(.white.opacity(0.9))
                    .multilineTextAlignment(.center)
                    .lineLimit(2)
                
                Spacer()
                
                // Progress indicator (simulate energy level)
                HStack {
                    Image(systemName: "sparkles")
                        .font(.caption2)
                    Text("∞ Possibilities")
                        .font(.caption2)
                        .fontWeight(.semibold)
                }
                .foregroundColor(.white.opacity(0.9))
            }
            .padding()
            .frame(height: 180)
            .background(
                LinearGradient(
                    colors: [.purple, .blue],
                    startPoint: .topLeading,
                    endPoint: .bottomTrailing
                )
            )
            .cornerRadius(12)
            .shadow(radius: 4)
        }
        .buttonStyle(PlainButtonStyle())
    }
}

// Enhanced Demo Video Card with AI option
struct EnhancedDemoVideoCard: View {
    let item: DemoVideoItem
    @State private var showAIVariation = false
    
    var body: some View {
        VStack {
            // Existing card design
            DemoVideoCard(item: item)
            
            // Add AI variation button
            Button("🤖 Create AI Variation") {
                showAIVariation = true
            }
            .font(.caption)
            .foregroundColor(.orange)
            .padding(.top, 4)
        }
        .sheet(isPresented: $showAIVariation) {
            AIMessageGeneratorView(
                // Pre-populate with this card's topic
                initialTopic: item.title
            )
        }
    }
}

// Updated AI Message Generator with initial topic support
extension AIMessageGeneratorView {
    init(initialTopic: String = "") {
        self._userInput = State(initialValue: initialTopic)
    }
}

#Preview {
    MainTabView()
} 