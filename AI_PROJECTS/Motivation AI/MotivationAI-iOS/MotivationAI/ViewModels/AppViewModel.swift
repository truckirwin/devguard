import Foundation
import SwiftUI

@MainActor
class AppViewModel: ObservableObject {
    @Published var isLoading = false
    @Published var currentUser: User?
    @Published var tasks: [Task] = []
    @Published var todaysMessage: DailyMessage?
    @Published var learningPaths: [LearningPath] = []
    @Published var userProgress: UserProgress?
    
    // MARK: - Published Properties
    @Published var selectedTab: Int = 0
    @Published var weeklyGoal: Int = 5
    @Published var currentStreak: Int = 3
    @Published var applications: [JobApplication] = []
    @Published var dailyTasks: [DailyTask] = []
    @Published var achievements: [Achievement] = []
    @Published var emergencyContacts: [EmergencyContact] = []
    @Published var therapistInfo: TherapistInfo?
    @Published var currentMood: MoodEntry?
    @Published var recentMoods: [MoodEntry] = []
    
    // MARK: - Message Display Properties (moved from MessageManager)
    @Published var isShowingAnimatedText: Bool = false
    @Published var currentMessage: MotivationalMessage?
    
    // MARK: - Settings
    @Published var isVoiceoverEnabled: Bool = true
    @Published var voiceoverSpeed: Double = 1.0
    @Published var notificationsEnabled: Bool = true
    
    // Message System - using AppViewModel directly instead of MessageManager
    
    init() {
        loadSampleData()
        setupDailyMessage()
        
        // Auto-play first message on app launch
        DispatchQueue.main.asyncAfter(deadline: .now() + 1.0) {
            self.showFirstMessage()
        }
    }
    
    // MARK: - Computed Properties for Dashboard
    var todaysTasks: [Task] {
        return tasks
    }
    
    var completedTasksToday: Int {
        return tasks.filter { $0.isCompleted }.count
    }
    
    var totalTasksToday: Int {
        return tasks.count
    }
    
    var inProgressLearningPaths: [LearningPath] {
        return learningPaths.filter { $0.progress > 0 && $0.progress < 1.0 }
    }
    
    var streakDays: Int {
        return 7 // Sample streak value
    }
    
    private func setupDailyMessage() {
        // Get today's contextual message from demo scripts
        let message = DemoVideoScripts.getRandomScript()
        todaysMessage = message
    }
    
    private func loadSampleData() {
        // Sample user
        currentUser = User(
            id: "1", 
            name: "John Doe",
            email: "john@example.com",
            plan: .free
        )
        
        // Sample tasks
        tasks = [
            Task(id: "1", title: "Update LinkedIn Profile", category: "Profile", priority: "High"),
            Task(id: "2", title: "Apply to 5 Jobs", category: "Applications", priority: "High"),
            Task(id: "3", title: "Practice Interview Questions", category: "Interview", priority: "Medium"),
            Task(id: "4", title: "Network with 2 People", category: "Networking", priority: "Medium")
        ]
        
        // Sample learning paths
        learningPaths = [
            LearningPath(
                id: "1",
                title: "AI Job Search Mastery",
                description: "Master modern job hunting with AI tools",
                category: .jobSearch,
                progress: 0.3
            ),
            LearningPath(
                id: "2",
                title: "Interview Excellence", 
                description: "Ace any interview with confidence",
                category: .interview,
                progress: 0.7
            )
        ]
        
        // Sample user progress
        userProgress = UserProgress(
            userId: "1",
            level: 3,
            experiencePoints: 250,
            tasksCompleted: 15,
            streakDays: 7,
            achievements: ["First Task", "LinkedIn Pro"]
        )
    }

    // MARK: - Task Management
    func addTask(_ task: Task) {
        tasks.append(task)
    }

    func toggleTaskCompletion(_ taskId: String) {
        if let index = tasks.firstIndex(where: { $0.id == taskId }) {
            let wasCompleted = tasks[index].isCompleted
            tasks[index].isCompleted.toggle()
            
            // Trigger celebration if task was just completed
            if !wasCompleted && tasks[index].isCompleted {
                // Could show a celebration message here
                print("🎉 Task completed!")
            }
        }
    }

    func deleteTask(_ taskId: String) {
        tasks.removeAll { $0.id == taskId }
    }
    
    // MARK: - Message System Integration
    func showFirstMessage() {
        let firstMessage = DemoVideoScripts.demoScripts.first!
        showAnimatedTextMessage(firstMessage)
    }
    
    func showDailyMessage() {
        let message = DemoVideoScripts.getRandomScript()
        showAnimatedTextMessage(message)
    }
    
    func showMotivationalBoost() {
        let toughLoveMessages = DemoVideoScripts.toughLoveScripts
        if let message = toughLoveMessages.randomElement() {
            showAnimatedTextMessage(message)
        }
    }
    
    func showCompassionateMessage() {
        let compassionateMessages = DemoVideoScripts.demoScripts.filter { $0.tone == .compassionate }
        if let message = compassionateMessages.randomElement() {
            showAnimatedTextMessage(message)
        }
    }
    
    func showActionOrientedMessage() {
        let actionMessages = DemoVideoScripts.demoScripts.filter { $0.tone == .actionFocused }
        if let message = actionMessages.randomElement() {
            showAnimatedTextMessage(message)
        }
    }
    
    // MARK: - Message Display Functions
    func showAnimatedTextMessage(_ message: MotivationalMessage) {
        currentMessage = message
        isShowingAnimatedText = true
        
        if isVoiceoverEnabled && message.audioEnabled {
            // For now, just set the message - speech synthesis can be added later
            print("🎬 Message set: \(message.title)")
        }
    }
    
    func dismissCurrentMessage() {
        currentMessage = nil
        isShowingAnimatedText = false
        print("🎬 Message dismissed")
    }
} 