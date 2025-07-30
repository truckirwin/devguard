import SwiftUI
import Contacts

struct ProfileView: View {
    @StateObject private var profileViewModel = ProfileViewModel()
    @State private var selectedTab = 0
    
    private let tabs = ["Personal Info", "App Preferences", "Daily Schedule"]
    
    var body: some View {
        NavigationView {
            VStack(spacing: 0) {
                // Tab bar at the top
                tabBar
                
                // Content based on selected tab
                ScrollView {
                    VStack(spacing: 20) {
                        switch selectedTab {
                        case 0:
                            personalInfoContent
                        case 1:
                            appPreferencesContent
                        case 2:
                            dailyScheduleContent
                        default:
                            personalInfoContent
                        }
                        
                        Spacer(minLength: 50)
                    }
                    .padding(.top, 20)
                }
            }
            .background(Color.black.ignoresSafeArea())
            .navigationTitle("")
            .navigationBarTitleDisplayMode(.inline)
            .preferredColorScheme(.dark)
        }
    }
    
    // MARK: - Tab Bar
    private var tabBar: some View {
        HStack(spacing: 0) {
            ForEach(0..<tabs.count, id: \.self) { index in
                Button(action: {
                    selectedTab = index
                }) {
                    VStack(spacing: 8) {
                        Text(tabs[index])
                            .font(.system(size: 16, weight: .medium))
                            .foregroundColor(selectedTab == index ? .white : .gray)
                        
                        Rectangle()
                            .fill(selectedTab == index ? Color.orange : Color.clear)
                            .frame(height: 2)
                    }
                }
                .frame(maxWidth: .infinity)
            }
        }
        .padding(.horizontal, 20)
        .padding(.top, 10)
        .background(Color.black)
    }
    
    // MARK: - Personal Info Content
    private var personalInfoContent: some View {
        VStack(spacing: 20) {
            ProfileInfoCard(icon: "person.fill", title: "Personal Info") {
                VStack(spacing: 16) {
                    InfoRow(label: "Name", value: "Robert Irwin")
                    InfoRow(label: "Age", value: "58")
                    InfoRow(label: "Experience", value: "26 years")
                    InfoRow(label: "Industry", value: "Hi Tech")
                    InfoRow(label: "Location", value: "Remote")
                }
            }
        }
        .padding(.horizontal, 20)
    }
    
    // MARK: - App Preferences Content
    private var appPreferencesContent: some View {
        VStack(spacing: 20) {
            ProfileInfoCard(icon: "gearshape.fill", title: "App Preferences") {
                VStack(spacing: 20) {
                    // Theme selection
                    VStack(alignment: .leading, spacing: 12) {
                        Text("Theme")
                            .font(.system(size: 16, weight: .medium))
                            .foregroundColor(.white)
                        
                        HStack(spacing: 12) {
                            ThemeButton(title: "Light", isSelected: false)
                            ThemeButton(title: "Dark", isSelected: true)
                            ThemeButton(title: "Chill", isSelected: false)
                            ThemeButton(title: "Warm", isSelected: false)
                        }
                    }
                    
                    // Coaching Style selection
                    VStack(alignment: .leading, spacing: 12) {
                        Text("Coaching Style")
                            .font(.system(size: 16, weight: .medium))
                            .foregroundColor(.white)
                        
                        HStack(spacing: 12) {
                            ThemeButton(title: "Chill", isSelected: false)
                            ThemeButton(title: "Counselor", isSelected: false)
                            ThemeButton(title: "Coach", isSelected: false)
                            ThemeButton(title: "Drill Sergeant", isSelected: true)
                        }
                    }
                    
                    // Task Intensity selection
                    VStack(alignment: .leading, spacing: 12) {
                        Text("Task Intensity")
                            .font(.system(size: 16, weight: .medium))
                            .foregroundColor(.white)
                        
                        HStack(spacing: 12) {
                            ThemeButton(title: "Light Load", isSelected: false)
                            ThemeButton(title: "Moderate", isSelected: false)
                            ThemeButton(title: "Heavy Load", isSelected: false)
                            ThemeButton(title: "Maximum", isSelected: true)
                        }
                        
                        Text("10+ tasks per day, all-out grind")
                            .font(.system(size: 12))
                            .foregroundColor(.gray)
                            .padding(.top, 4)
                    }
                }
            }
        }
        .padding(.horizontal, 20)
    }
    
    // MARK: - Daily Schedule Content
    private var dailyScheduleContent: some View {
        VStack(spacing: 20) {
            ProfileInfoCard(icon: "clock.fill", title: "Daily Schedule") {
                VStack(spacing: 16) {
                    ScheduleRow(title: "Wake Up", time: "7:00 AM")
                    ScheduleRow(title: "Mid-Day Check-in", time: "12:00 PM")
                    ScheduleRow(title: "Afternoon Wrap", time: "5:00 PM")
                    ScheduleRow(title: "Goodnight", time: "9:00 PM")
                }
            }
        }
        .padding(.horizontal, 20)
    }
}

// MARK: - Profile Info Card
struct ProfileInfoCard<Content: View>: View {
    let icon: String
    let title: String
    let content: () -> Content
    
    var body: some View {
        VStack(alignment: .leading, spacing: 16) {
            HStack {
                Image(systemName: icon)
                    .foregroundColor(.orange)
                    .font(.system(size: 20, weight: .medium))
                
                Text(title)
                    .font(.system(size: 18, weight: .semibold))
                    .foregroundColor(.white)
                
                Spacer()
            }
            
            content()
        }
        .padding(20)
        .background(Color.gray.opacity(0.1))
        .cornerRadius(12)
    }
}

// MARK: - Info Row
struct InfoRow: View {
    let label: String
    let value: String
    
    var body: some View {
        HStack {
            Text(label)
                .font(.system(size: 16, weight: .medium))
                .foregroundColor(.white)
            
            Spacer()
            
            Text(value)
                .font(.system(size: 16, weight: .medium))
                .foregroundColor(.white)
        }
    }
}

// MARK: - Theme Button
struct ThemeButton: View {
    let title: String
    let isSelected: Bool
    
    var body: some View {
        Text(title)
            .font(.system(size: 14, weight: .medium))
            .foregroundColor(isSelected ? .black : .white)
            .padding(.horizontal, 16)
            .padding(.vertical, 8)
            .background(isSelected ? Color.orange : Color.gray.opacity(0.3))
            .cornerRadius(20)
    }
}

// MARK: - Schedule Row
struct ScheduleRow: View {
    let title: String
    let time: String
    
    var body: some View {
        HStack {
            Text(title)
                .font(.system(size: 16, weight: .medium))
                .foregroundColor(.white)
            
            Spacer()
            
            Text(time)
                .font(.system(size: 16, weight: .medium))
                .foregroundColor(.white)
                .padding(.horizontal, 12)
                .padding(.vertical, 6)
                .background(Color.gray.opacity(0.3))
                .cornerRadius(8)
        }
    }
}

#Preview {
    ProfileView()
        .preferredColorScheme(.dark)
}