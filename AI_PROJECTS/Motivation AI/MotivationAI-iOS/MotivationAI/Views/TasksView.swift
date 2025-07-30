import SwiftUI

struct TasksView: View {
    @EnvironmentObject var appViewModel: AppViewModel
    @EnvironmentObject var profileManager: ProfileManager
    @StateObject private var taskManager = TaskManager()
    @State private var selectedFrequency: TaskFrequency = .daily
    @State private var showAddTaskSheet = false
    
    var body: some View {
        NavigationView {
            ZStack {
                // Pure black background - no grays
                Color(red: 0, green: 0, blue: 0)
                    .ignoresSafeArea()
                
                ScrollView {
                    VStack(spacing: 16) { // Reduced from 24
                        // Command center header - minimal spacing
                        commandCenterHeader
                        
                        // Focus rings - tight spacing
                        if selectedFrequency == .daily && !taskManager.progressRings.isEmpty {
                            focusRingsSection
                        }
                        
                        // Frequency selector - minimal padding
                        frequencySelector
                        
                        // Tasks list - tight layout
                        tasksSection
                        
                        Spacer(minLength: 50) // Reduced from 100
                    }
                }
            }
            .navigationTitle("")
            .navigationBarTitleDisplayMode(.inline)
            .preferredColorScheme(.dark)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button(action: {
                        taskManager.generateTasks()
                    }) {
                        Image(systemName: "arrow.clockwise")
                            .foregroundColor(.white)
                            .font(.title3)
                    }
                }
            }
        }
        .onAppear {
            taskManager.generateTasks()
        }
    }
    
    // MARK: - Command Center Header (Minimal Spacing)
    private var commandCenterHeader: some View {
        VStack(spacing: 8) { // Reduced from 16
            HStack {
                VStack(alignment: .leading, spacing: 2) { // Reduced from 4
                    Text(personalizedHeaderTitle)
                        .font(.system(size: 24, weight: .bold))
                        .foregroundColor(.white)
                    
                    Text(personalizedSubtitle)
                        .font(.system(size: 16, weight: .medium))
                        .foregroundColor(.white.opacity(0.7))
                }
                
                Spacer()
                
                // Completion percentage - orange highlight
                Text("\(completionPercentage)%")
                    .font(.system(size: 32, weight: .heavy))
                    .foregroundColor(.orange)
            }
            .padding(.horizontal, 16) // Reduced from 20
            .padding(.top, 8) // Reduced from 20
            
            // Personalized coaching message
            if completionPercentage > 0 {
                Text(personalizedCoachingMessage)
                    .font(.system(size: 14, weight: .medium))
                    .foregroundColor(.orange.opacity(0.8))
                    .padding(.horizontal, 16)
                    .multilineTextAlignment(.leading)
            }
        }
    }
    
    // MARK: - Personalized Content
    private var personalizedHeaderTitle: String {
        switch profileManager.userProfile.preferences.coachingStyle {
        case .chill:
            return "Your Journey"
        case .counselor:
            return "Progress Center"
        case .coach:
            return "Command Center"
        case .drillSergeant:
            return "Mission Control"
        }
    }
    
    private var personalizedSubtitle: String {
        let intensity = profileManager.userProfile.preferences.taskIntensity
        switch profileManager.userProfile.preferences.coachingStyle {
        case .chill:
            return "Take it one step at a time"
        case .counselor:
            return "You're doing great, keep going"
        case .coach:
            return "Today's mission (\(intensity.rawValue))"
        case .drillSergeant:
            return "EXECUTE THE MISSION"
        }
    }
    
    private var personalizedCoachingMessage: String {
        let style = profileManager.userProfile.preferences.coachingStyle
        let percentage = completionPercentage
        
        switch style {
        case .chill:
            if percentage < 25 { return "🌱 Starting is the hardest part - you've got this" }
            else if percentage < 50 { return "🌿 Nice flow! Keep that peaceful energy going" }
            else if percentage < 75 { return "🌳 Beautiful progress - feel that momentum building" }
            else { return "🧘‍♀️ Amazing work! You're in perfect harmony today" }
            
        case .counselor:
            if percentage < 25 { return "💛 Every small step matters - I believe in you" }
            else if percentage < 50 { return "💫 You're stronger than you know - keep pushing" }
            else if percentage < 75 { return "✨ Look how far you've come! I'm proud of you" }
            else { return "🌟 Incredible work! You should feel so proud today" }
            
        case .coach:
            if percentage < 25 { return "💪 Let's build that momentum - you've got this!" }
            else if percentage < 50 { return "🔥 Great hustle! Keep that energy up!" }
            else if percentage < 75 { return "⚡ Outstanding! Push through to the finish!" }
            else { return "🏆 CHAMPION LEVEL! You absolutely crushed it!" }
            
        case .drillSergeant:
            if percentage < 25 { return "⚡ MOVE IT! Those tasks won't complete themselves!" }
            else if percentage < 50 { return "🎯 STAY FOCUSED! No room for slacking!" }
            else if percentage < 75 { return "💥 PUSH HARDER! Victory is within reach!" }
            else { return "🔥 MISSION ACCOMPLISHED! You're unstoppable!" }
        }
    }
    
    // MARK: - Focus Rings (Tight Layout)
    private var focusRingsSection: some View {
        VStack(spacing: 8) { // Reduced from 16
            Text("Focus Areas")
                .font(.system(size: 18, weight: .semibold))
                .foregroundColor(.white)
                .frame(maxWidth: .infinity, alignment: .leading)
                .padding(.horizontal, 16) // Reduced from 20
            
            HStack(spacing: 20) { // Reduced from 30
                ForEach(focusAreaRings, id: \.id) { ring in
                    VStack(spacing: 8) { // Reduced from 12
                        ZStack {
                            Circle()
                                .stroke(Color.white.opacity(0.1), lineWidth: 4) // Reduced from 6
                                .frame(width: 70, height: 70) // Reduced from 80
                            
                            Circle()
                                .trim(from: 0, to: ring.progress)
                                .stroke(ringColor(for: ring.category), lineWidth: 4) // Reduced from 6
                                .frame(width: 70, height: 70) // Reduced from 80
                                .rotationEffect(.degrees(-90))
                            
                            VStack(spacing: 1) { // Reduced from 2
                                Text("\(ring.current)")
                                    .font(.system(size: 18, weight: .bold)) // Reduced from 20
                                    .foregroundColor(.white)
                                Text("of \(ring.target)")
                                    .font(.system(size: 9)) // Reduced from 10
                                    .foregroundColor(.white.opacity(0.6))
                            }
                        }
                        
                        Text(ring.category.name)
                            .font(.system(size: 12, weight: .medium)) // Reduced from 14
                            .foregroundColor(.white)
                    }
                }
            }
            .padding(.horizontal, 16) // Reduced from 20
        }
    }
    
    // MARK: - Frequency Selector (Minimal)
    private var frequencySelector: some View {
        HStack(spacing: 0) {
            ForEach(TaskFrequency.allCases, id: \.self) { frequency in
                Button(action: {
                    selectedFrequency = frequency
                }) {
                    VStack(spacing: 4) { // Reduced from 6
                        Text(frequency.rawValue)
                            .font(.system(size: 13, weight: .semibold)) // Reduced from 14
                            .foregroundColor(selectedFrequency == frequency ? .black : .white.opacity(0.7))
                        
                        Text("\(taskCount(for: frequency))")
                            .font(.system(size: 16, weight: .bold)) // Reduced from 18
                            .foregroundColor(selectedFrequency == frequency ? .black : .orange)
                    }
                    .frame(maxWidth: .infinity)
                    .frame(height: 50) // Reduced from 60
                    .background(
                        RoundedRectangle(cornerRadius: 8) // Reduced from 12
                            .fill(selectedFrequency == frequency ? .orange : Color.clear)
                    )
                }
                .buttonStyle(PlainButtonStyle())
            }
        }
        .padding(.horizontal, 16) // Reduced from 20
    }
    
    // MARK: - Tasks Section (Tight Layout)
    private var tasksSection: some View {
        VStack(spacing: 8) { // Reduced from 16
            HStack {
                Text("\(selectedFrequency.rawValue) Tasks")
                    .font(.system(size: 16, weight: .semibold)) // Reduced from 18
                    .foregroundColor(.white)
                
                Spacer()
                
                Text("\(currentTasks.count)")
                    .font(.system(size: 14, weight: .bold)) // Reduced from 16
                    .foregroundColor(.orange)
            }
            .padding(.horizontal, 16) // Reduced from 20
            
            LazyVStack(spacing: 6) { // Reduced from 12
                ForEach(currentTasks) { task in
                    BlackTaskCard(
                        task: task,
                        onToggle: { taskManager.toggleTaskCompletion($0) }
                    )
                }
            }
            .padding(.horizontal, 16) // Reduced from 20
        }
    }
    
    // MARK: - Helper Properties
    private var currentTasks: [DailyTask] {
        switch selectedFrequency {
        case .daily: return taskManager.todaysTasks
        case .weekly: return taskManager.weeklyTasks
        case .monthly: return taskManager.monthlyTasks
        case .anytime: return taskManager.anytimeTasks
        }
    }
    
    private var completionPercentage: Int {
        let completed = currentTasks.filter { $0.status == .completed }.count
        let total = currentTasks.count
        return total > 0 ? Int((Double(completed) / Double(total)) * 100) : 0
    }
    
    private func taskCount(for frequency: TaskFrequency) -> Int {
        switch frequency {
        case .daily: return taskManager.todaysTasks.count
        case .weekly: return taskManager.weeklyTasks.count
        case .monthly: return taskManager.monthlyTasks.count
        case .anytime: return taskManager.anytimeTasks.count
        }
    }
    
    private func ringColor(for category: RingCategory) -> Color {
        switch category {
        case .hustle: return .orange
        case .grind: return .red
        case .skills: return .blue
        }
    }
    
    // Sample focus area rings
    private var focusAreaRings: [TaskProgressRingData] {
        [
            TaskProgressRingData(id: "hustle", category: .hustle, progress: 0.7, target: 5, current: 3),
            TaskProgressRingData(id: "grind", category: .grind, progress: 0.5, target: 4, current: 2),
            TaskProgressRingData(id: "skills", category: .skills, progress: 0.3, target: 3, current: 1)
        ]
    }
}

// MARK: - Black Task Card (Pure Black Design)
struct BlackTaskCard: View {
    let task: DailyTask
    let onToggle: (DailyTask) -> Void
    
    var body: some View {
        HStack(spacing: 12) { // Reduced from 16
            // Completion circle - color highlight only
            Button(action: { onToggle(task) }) {
                ZStack {
                    Circle()
                        .stroke(task.status == .completed ? .green : .white.opacity(0.3), lineWidth: 2)
                        .frame(width: 20, height: 20) // Reduced from 24
                    
                    if task.status == .completed {
                        Image(systemName: "checkmark")
                            .font(.system(size: 10, weight: .bold)) // Reduced from 12
                            .foregroundColor(.green)
                    }
                }
            }
            .buttonStyle(PlainButtonStyle())
            
            // Task content - white text on black
            VStack(alignment: .leading, spacing: 2) { // Reduced from 4
                Text(task.title)
                    .font(.system(size: 14, weight: .medium)) // Reduced from 16
                    .foregroundColor(.white)
                    .strikethrough(task.status == .completed)
                
                if !task.description.isEmpty {
                    Text(task.description)
                        .font(.system(size: 12)) // Reduced from 14
                        .foregroundColor(.white.opacity(0.6))
                        .lineLimit(2)
                }
            }
            
            Spacer()
            
            // Category color indicator
            categoryIndicator
        }
        .padding(.vertical, 10) // Reduced from 16
        // NO background - pure black with content floating
    }
    
    private var categoryIndicator: some View {
        Circle()
            .fill(categoryColor)
            .frame(width: 6, height: 6) // Reduced from 8
    }
    
    private var categoryColor: Color {
        switch task.category {
        case .hustle: return .orange
        case .grind: return .red
        case .skills: return .blue
        }
    }
}

// MARK: - Simple Ring Data Model
struct TaskProgressRingData: Identifiable {
    let id: String
    let category: RingCategory
    let progress: Double
    let target: Int
    let current: Int
}

#Preview {
    TasksView()
        .environmentObject(AppViewModel())
        .environmentObject(ProfileManager())
        .preferredColorScheme(.dark)
} 