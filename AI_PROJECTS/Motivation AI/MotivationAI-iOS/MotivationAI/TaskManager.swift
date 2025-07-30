import Foundation

class TaskManager: ObservableObject {
    // MARK: - Published Properties
    @Published var todaysTasks: [DailyTask] = []
    @Published var weeklyTasks: [DailyTask] = []
    @Published var monthlyTasks: [DailyTask] = []
    @Published var anytimeTasks: [DailyTask] = []
    @Published var progressRings: [TaskProgressRing] = []
    @Published var currentStreak: Int = 0
    @Published var isLoading: Bool = false
    
    // MARK: - Private Properties
    private let userDefaults = UserDefaults.standard
    private let tasksKey = "DailyTasks"
    private let weeklyTasksKey = "WeeklyTasks"
    private let monthlyTasksKey = "MonthlyTasks"
    private let anytimeTasksKey = "AnytimeTasks"
    private let streakKey = "CurrentStreak"
    private let lastDateKey = "LastTaskDate"
    
    // MARK: - Enhanced Task Templates
    private let taskTemplates: [TaskTemplate] = [
        // Daily Tasks - Hustle (Career Focus)
        TaskTemplate(title: "Apply to 3 Jobs", description: "Submit applications to new job opportunities", category: .hustle, frequency: .daily, estimatedTimeMinutes: 45, difficulty: .medium, tags: ["job-search", "applications"]),
        TaskTemplate(title: "Update LinkedIn", description: "Add a post, connection, or update your profile", category: .hustle, frequency: .daily, estimatedTimeMinutes: 15, difficulty: .easy, tags: ["networking", "linkedin"]),
        TaskTemplate(title: "Send Follow-up Email", description: "Follow up on applications or networking contacts", category: .hustle, frequency: .daily, estimatedTimeMinutes: 10, difficulty: .easy, tags: ["follow-up", "email"]),
        
        // Daily Tasks - Grind (Work Ethic)
        TaskTemplate(title: "Take 8,000 Steps", description: "Reach your daily step goal", category: .grind, frequency: .daily, estimatedTimeMinutes: 60, difficulty: .easy, tags: ["cardio", "walking"], fitnessIntegration: FitnessIntegration.stepCount),
        TaskTemplate(title: "Exercise for 30 Minutes", description: "Complete 30 minutes of active exercise", category: .grind, frequency: .daily, estimatedTimeMinutes: 30, difficulty: .medium, tags: ["exercise", "fitness"], fitnessIntegration: FitnessIntegration.exerciseTime),
        TaskTemplate(title: "Burn 300 Active Calories", description: "Reach your active energy goal", category: .grind, frequency: .daily, estimatedTimeMinutes: 45, difficulty: .medium, tags: ["cardio", "calories"], fitnessIntegration: FitnessIntegration.activeEnergy),
        TaskTemplate(title: "Drink 8 Glasses of Water", description: "Stay hydrated throughout the day", category: .grind, frequency: .daily, estimatedTimeMinutes: 5, difficulty: .easy, tags: ["hydration", "wellness"]),
        TaskTemplate(title: "Eat a Healthy Lunch", description: "Prepare or choose a nutritious meal", category: .grind, frequency: .daily, estimatedTimeMinutes: 20, difficulty: .easy, tags: ["nutrition", "meal"]),
        TaskTemplate(title: "Stretch for 10 Minutes", description: "Do stretching exercises to relieve tension", category: .grind, frequency: .daily, estimatedTimeMinutes: 10, difficulty: .easy, tags: ["flexibility", "recovery"]),
        
        // Weekly Tasks - Grind (Work Ethic)
        TaskTemplate(title: "Meal Prep for the Week", description: "Prepare healthy meals and snacks", category: .grind, frequency: .weekly, estimatedTimeMinutes: 120, difficulty: .medium, tags: ["meal-prep", "nutrition"]),
        TaskTemplate(title: "Complete Long Workout", description: "Do a comprehensive 60-90 minute workout", category: .grind, frequency: .weekly, estimatedTimeMinutes: 75, difficulty: .hard, tags: ["exercise", "fitness"]),
        TaskTemplate(title: "Try New Healthy Recipe", description: "Cook a nutritious meal you've never made before", category: .grind, frequency: .weekly, estimatedTimeMinutes: 45, difficulty: .medium, tags: ["cooking", "nutrition"]),
        
        // Monthly Tasks - Grind (Work Ethic)
        TaskTemplate(title: "Health Check-up", description: "Schedule and attend routine health appointments", category: .grind, frequency: .monthly, estimatedTimeMinutes: 120, difficulty: .medium, tags: ["health", "medical"]),
        TaskTemplate(title: "Fitness Goal Assessment", description: "Review and adjust your fitness goals", category: .grind, frequency: .monthly, estimatedTimeMinutes: 30, difficulty: .easy, tags: ["goals", "fitness"]),
        
        // Daily Tasks - Skills (Learning)
        TaskTemplate(title: "Meditate for 10 Minutes", description: "Practice mindfulness or breathing exercises", category: .skills, frequency: .daily, estimatedTimeMinutes: 10, difficulty: .easy, tags: ["meditation", "mindfulness"]),
        TaskTemplate(title: "Journal", description: "Write about your thoughts, goals, or gratitude", category: .skills, frequency: .daily, estimatedTimeMinutes: 15, difficulty: .easy, tags: ["journaling", "reflection"]),
        TaskTemplate(title: "Read for 20 Minutes", description: "Read a book, article, or personal development content", category: .skills, frequency: .daily, estimatedTimeMinutes: 20, difficulty: .easy, tags: ["reading", "learning"]),
        TaskTemplate(title: "Practice Gratitude", description: "List 3 things you're grateful for today", category: .skills, frequency: .daily, estimatedTimeMinutes: 5, difficulty: .easy, tags: ["gratitude", "positivity"]),
        TaskTemplate(title: "Practice Deep Breathing", description: "Do 5 minutes of focused breathing exercises", category: .skills, frequency: .daily, estimatedTimeMinutes: 5, difficulty: .easy, tags: ["breathing", "relaxation"]),
        
        // Weekly Tasks - Skills (Learning)
        TaskTemplate(title: "Listen to Educational Podcast", description: "Listen to a full podcast episode about career or personal development", category: .skills, frequency: .weekly, estimatedTimeMinutes: 45, difficulty: .easy, tags: ["podcast", "learning"]),
        TaskTemplate(title: "Connect with Friend/Family", description: "Have a meaningful conversation with someone you care about", category: .skills, frequency: .weekly, estimatedTimeMinutes: 30, difficulty: .medium, tags: ["social", "connection"]),
        TaskTemplate(title: "Plan Next Week", description: "Review goals and plan tasks for the upcoming week", category: .skills, frequency: .weekly, estimatedTimeMinutes: 20, difficulty: .easy, tags: ["planning", "goals"]),
        
        // Monthly Tasks - Skills (Learning)
        TaskTemplate(title: "Complete Online Course Module", description: "Finish a section of an online course or certification", category: .skills, frequency: .monthly, estimatedTimeMinutes: 180, difficulty: .medium, tags: ["learning", "skills"]),
        TaskTemplate(title: "Monthly Reflection", description: "Deep reflection on progress, goals, and mental well-being", category: .skills, frequency: .monthly, estimatedTimeMinutes: 45, difficulty: .medium, tags: ["reflection", "goals"]),
        
        // Anytime Tasks - Mixed
        TaskTemplate(title: "Learn Something New", description: "Spend time learning a new skill, fact, or concept", category: .skills, frequency: .anytime, estimatedTimeMinutes: 25, difficulty: .medium, tags: ["learning", "growth"]),
        TaskTemplate(title: "Quick Exercise", description: "Do a 15-minute workout or physical activity", category: .grind, frequency: .anytime, estimatedTimeMinutes: 15, difficulty: .easy, tags: ["exercise", "fitness"]),
        TaskTemplate(title: "Eat a Healthy Snack", description: "Choose a nutritious snack over processed food", category: .grind, frequency: .anytime, estimatedTimeMinutes: 5, difficulty: .easy, tags: ["nutrition", "snack"]),
        TaskTemplate(title: "Practice Mindfulness", description: "Take a mindful moment to center yourself", category: .skills, frequency: .anytime, estimatedTimeMinutes: 5, difficulty: .easy, tags: ["mindfulness", "mental-health"]),
        TaskTemplate(title: "Send Encouraging Message", description: "Reach out to someone with a supportive message", category: .skills, frequency: .anytime, estimatedTimeMinutes: 5, difficulty: .easy, tags: ["social", "kindness"]),
    ]
    
    // MARK: - Initialization
    init() {
        loadAllTasks()
        updateProgressRings()
        checkStreak()
    }
    
    // MARK: - Public Methods
    func generateTasks() {
        generateTodaysTasks()
        generateWeeklyTasks()
        generateMonthlyTasks()
        generateAnytimeTasks()
        updateProgressRings()
    }
    
    func generateTodaysTasks() {
        generateTasksForFrequency(.daily)
    }
    
    func generateWeeklyTasks() {
        generateTasksForFrequency(.weekly)
    }
    
    func generateMonthlyTasks() {
        generateTasksForFrequency(.monthly)
    }
    
    func generateAnytimeTasks() {
        generateTasksForFrequency(.anytime)
    }
    
    func toggleTaskCompletion(_ task: DailyTask) {
        let newStatus: TaskStatus = task.status == .completed ? .pending : .completed
        updateTaskStatus(task, status: newStatus)
        updateProgressRings()
        checkStreak()
    }
    
    func deleteTask(_ task: DailyTask) {
        // Remove from appropriate array
        if let index = todaysTasks.firstIndex(where: { $0.id == task.id }) {
            todaysTasks.remove(at: index)
            saveTasks(for: .daily)
        } else if let index = weeklyTasks.firstIndex(where: { $0.id == task.id }) {
            weeklyTasks.remove(at: index)
            saveTasks(for: .weekly)
        } else if let index = monthlyTasks.firstIndex(where: { $0.id == task.id }) {
            monthlyTasks.remove(at: index)
            saveTasks(for: .monthly)
        } else if let index = anytimeTasks.firstIndex(where: { $0.id == task.id }) {
            anytimeTasks.remove(at: index)
            saveTasks(for: .anytime)
        }
        updateProgressRings()
    }
    
    private func generateTasksForFrequency(_ frequency: TaskFrequency) {
        let today = Date()
        let calendar = Calendar.current
        
        // Get appropriate task array and check if we need to generate
        switch frequency {
        case .daily:
            if let existingTask = todaysTasks.first,
               calendar.isDate(existingTask.date, inSameDayAs: today) {
                return // Already have tasks for today
            }
            todaysTasks.removeAll()
            
        case .weekly:
            if let existingTask = weeklyTasks.first,
               calendar.isDate(existingTask.date, equalTo: today, toGranularity: .weekOfYear) {
                return // Already have tasks for this week
            }
            weeklyTasks.removeAll()
            
        case .monthly:
            if let existingTask = monthlyTasks.first,
               calendar.isDate(existingTask.date, equalTo: today, toGranularity: .month) {
                return // Already have tasks for this month
            }
            monthlyTasks.removeAll()
            
        case .anytime:
            if anytimeTasks.count >= 6 { // Keep 6 anytime tasks available
                return
            }
        }
        
        // Generate tasks for each category
        var newTasks: [DailyTask] = []
        let frequencyTemplates = taskTemplates.filter { $0.frequency == frequency }
        
        let taskCounts = switch frequency {
        case .daily: (hustle: 3, grind: 2, skills: 2)
        case .weekly: (hustle: 2, grind: 1, skills: 1)
        case .monthly: (hustle: 1, grind: 1, skills: 1)
        case .anytime: (hustle: 2, grind: 2, skills: 2)
        }
        
        // HUSTLE tasks
        let hustleTasks = frequencyTemplates.filter { $0.category == .hustle }.shuffled().prefix(taskCounts.hustle)
        newTasks += hustleTasks.map { DailyTask(from: $0, date: today) }
        
        // GRIND tasks
        let grindTasks = frequencyTemplates.filter { $0.category == .grind }.shuffled().prefix(taskCounts.grind)
        newTasks += grindTasks.map { DailyTask(from: $0, date: today) }
        
        // SKILLS tasks
        let skillsTasks = frequencyTemplates.filter { $0.category == .skills }.shuffled().prefix(taskCounts.skills)
        newTasks += skillsTasks.map { DailyTask(from: $0, date: today) }
        
        // Assign to appropriate array
        switch frequency {
        case .daily:
            todaysTasks = newTasks
            saveTasks(for: .daily)
        case .weekly:
            weeklyTasks = newTasks
            saveTasks(for: .weekly)
        case .monthly:
            monthlyTasks = newTasks
            saveTasks(for: .monthly)
        case .anytime:
            anytimeTasks.append(contentsOf: newTasks)
            saveTasks(for: .anytime)
        }
        
        updateProgressRings()
    }
    
    func completeTask(_ task: DailyTask) {
        updateTaskStatus(task, status: .completed)
    }
    
    func skipTask(_ task: DailyTask) {
        updateTaskStatus(task, status: .skipped)
    }
    
    func resetTask(_ task: DailyTask) {
        updateTaskStatus(task, status: .pending)
    }
    
    private func updateTaskStatus(_ task: DailyTask, status: TaskStatus) {
        // Update task in the appropriate array
        if let index = todaysTasks.firstIndex(where: { $0.id == task.id }) {
            todaysTasks[index].status = status
            todaysTasks[index].completedAt = status == .completed ? Date() : nil
            saveTasks(for: .daily)
        } else if let index = weeklyTasks.firstIndex(where: { $0.id == task.id }) {
            weeklyTasks[index].status = status
            weeklyTasks[index].completedAt = status == .completed ? Date() : nil
            saveTasks(for: .weekly)
        } else if let index = monthlyTasks.firstIndex(where: { $0.id == task.id }) {
            monthlyTasks[index].status = status
            monthlyTasks[index].completedAt = status == .completed ? Date() : nil
            saveTasks(for: .monthly)
        } else if let index = anytimeTasks.firstIndex(where: { $0.id == task.id }) {
            anytimeTasks[index].status = status
            anytimeTasks[index].completedAt = status == .completed ? Date() : nil
            saveTasks(for: .anytime)
        }
        
        updateProgressRings()
        checkStreak()
    }
    
    func addCustomTask(title: String, description: String, category: RingCategory, estimatedTime: Int, frequency: TaskFrequency = .anytime) {
        let template = TaskTemplate(
            title: title,
            description: description,
            category: category,
            frequency: frequency,
            estimatedTimeMinutes: estimatedTime,
            difficulty: .medium
        )
        
        let customTask = DailyTask(from: template, date: Date())
        
        switch frequency {
        case .daily:
            todaysTasks.append(customTask)
        case .weekly:
            weeklyTasks.append(customTask)
        case .monthly:
            monthlyTasks.append(customTask)
        case .anytime:
            anytimeTasks.append(customTask)
        }
        
        saveTasks(for: frequency)
        updateProgressRings()
    }
    
    // MARK: - Private Methods
    private func updateProgressRings() {
        // Daily rings
        let dailyHustleCompleted = todaysTasks.filter { $0.category == .hustle && $0.isCompleted }.count
        let dailyHustleTotal = todaysTasks.filter { $0.category == .hustle }.count
        
        let dailyGrindCompleted = todaysTasks.filter { $0.category == .grind && $0.isCompleted }.count
        let dailyGrindTotal = todaysTasks.filter { $0.category == .grind }.count
        
        let dailySkillsCompleted = todaysTasks.filter { $0.category == .skills && $0.isCompleted }.count
        let dailySkillsTotal = todaysTasks.filter { $0.category == .skills }.count
        
        progressRings = [
            TaskProgressRing(category: .hustle, completedTasks: dailyHustleCompleted, totalTasks: dailyHustleTotal, frequency: .daily),
            TaskProgressRing(category: .grind, completedTasks: dailyGrindCompleted, totalTasks: dailyGrindTotal, frequency: .daily),
            TaskProgressRing(category: .skills, completedTasks: dailySkillsCompleted, totalTasks: dailySkillsTotal, frequency: .daily)
        ]
    }
    
    private func checkStreak() {
        let today = Date()
        let calendar = Calendar.current
        
        // Check if all minimum targets are met today
        let hustleTarget = todaysTasks.filter { $0.category == .hustle && $0.isCompleted }.count >= RingCategory.hustle.minimumDailyTasks
        let grindTarget = todaysTasks.filter { $0.category == .grind && $0.isCompleted }.count >= RingCategory.grind.minimumDailyTasks
        let skillsTarget = todaysTasks.filter { $0.category == .skills && $0.isCompleted }.count >= RingCategory.skills.minimumDailyTasks
        
        let allTargetsMet = hustleTarget && grindTarget && skillsTarget
        
        if let lastDate = userDefaults.object(forKey: lastDateKey) as? Date {
            if calendar.isDate(lastDate, inSameDayAs: today) {
                // Same day, update streak if targets met
                if allTargetsMet {
                    currentStreak = userDefaults.integer(forKey: streakKey)
                }
            } else if calendar.isDate(lastDate, inSameDayAs: calendar.date(byAdding: .day, value: -1, to: today)!) {
                // Yesterday - continue or break streak
                if allTargetsMet {
                    currentStreak += 1
                    userDefaults.set(currentStreak, forKey: streakKey)
                } else {
                    currentStreak = 0
                    userDefaults.set(0, forKey: streakKey)
                }
                userDefaults.set(today, forKey: lastDateKey)
            } else {
                // Gap in days - reset streak
                currentStreak = allTargetsMet ? 1 : 0
                userDefaults.set(currentStreak, forKey: streakKey)
                userDefaults.set(today, forKey: lastDateKey)
            }
        } else {
            // First time
            currentStreak = allTargetsMet ? 1 : 0
            userDefaults.set(currentStreak, forKey: streakKey)
            userDefaults.set(today, forKey: lastDateKey)
        }
    }
    
    private func saveTasks(for frequency: TaskFrequency) {
        let key = switch frequency {
        case .daily: tasksKey
        case .weekly: weeklyTasksKey
        case .monthly: monthlyTasksKey
        case .anytime: anytimeTasksKey
        }
        
        let tasks = switch frequency {
        case .daily: todaysTasks
        case .weekly: weeklyTasks
        case .monthly: monthlyTasks
        case .anytime: anytimeTasks
        }
        
        if let data = try? JSONEncoder().encode(tasks) {
            userDefaults.set(data, forKey: key)
        }
    }
    
    private func loadAllTasks() {
        loadTasks(for: .daily)
        loadTasks(for: .weekly)
        loadTasks(for: .monthly)
        loadTasks(for: .anytime)
        
        currentStreak = userDefaults.integer(forKey: streakKey)
    }
    
    private func loadTasks(for frequency: TaskFrequency) {
        let key = switch frequency {
        case .daily: tasksKey
        case .weekly: weeklyTasksKey
        case .monthly: monthlyTasksKey
        case .anytime: anytimeTasksKey
        }
        
        if let data = userDefaults.data(forKey: key),
           let tasks = try? JSONDecoder().decode([DailyTask].self, from: data) {
            
            let today = Date()
            let calendar = Calendar.current
            
            // Check if tasks are still relevant
            let isRelevant = switch frequency {
            case .daily:
                if let firstTask = tasks.first {
                    calendar.isDate(firstTask.date, inSameDayAs: today)
                } else { false }
            case .weekly:
                if let firstTask = tasks.first {
                    calendar.isDate(firstTask.date, equalTo: today, toGranularity: .weekOfYear)
                } else { false }
            case .monthly:
                if let firstTask = tasks.first {
                    calendar.isDate(firstTask.date, equalTo: today, toGranularity: .month)
                } else { false }
            case .anytime:
                true // Anytime tasks persist
            }
            
            if isRelevant {
                switch frequency {
                case .daily: todaysTasks = tasks
                case .weekly: weeklyTasks = tasks
                case .monthly: monthlyTasks = tasks
                case .anytime: anytimeTasks = tasks
                }
            } else {
                // Tasks are old, generate new ones
                generateTasksForFrequency(frequency)
            }
        } else {
            // No saved tasks, generate new ones
            generateTasksForFrequency(frequency)
        }
    }
} 