import Foundation
import HealthKit
import UIKit

// MARK: - Legacy Compatibility Types
// Compatibility wrapper for existing AppViewModel
struct Task: Identifiable {
    let id: String
    let title: String
    let category: String
    let priority: String
    var isCompleted: Bool = false
    var description: String? = nil
    
    init(id: String = UUID().uuidString, title: String, category: String, priority: String, isCompleted: Bool = false, description: String? = nil) {
        self.id = id
        self.title = title
        self.category = category
        self.priority = priority
        self.isCompleted = isCompleted
        self.description = description
    }
}

// MARK: - Task Frequency Types
enum TaskFrequency: String, CaseIterable, Codable {
    case daily = "Daily"
    case weekly = "Weekly"
    case monthly = "Monthly"
    case anytime = "Anytime"
    
    var icon: String {
        switch self {
        case .daily: return "calendar"
        case .weekly: return "calendar.badge.clock"
        case .monthly: return "calendar.badge.exclamationmark"
        case .anytime: return "infinity"
        }
    }
    
    var color: String {
        switch self {
        case .daily: return "blue"
        case .weekly: return "green"
        case .monthly: return "orange"
        case .anytime: return "purple"
        }
    }
}

// MARK: - Three Ring System Models
enum RingCategory: String, CaseIterable, Codable {
    case hustle = "Hustle"
    case grind = "Grind"
    case skills = "Skills"
    
    var name: String {
        return self.rawValue
    }
    
    var subtitle: String {
        switch self {
        case .hustle: return "Career Focus"
        case .grind: return "Work Ethic"
        case .skills: return "Learning"
        }
    }
    
    var color: UIColor {
        switch self {
        case .hustle: return UIColor.systemOrange
        case .grind: return UIColor.systemRed
        case .skills: return UIColor.systemBlue
        }
    }
    
    var icon: String {
        switch self {
        case .hustle: return "briefcase.fill"
        case .grind: return "flame.fill"
        case .skills: return "brain.head.profile"
        }
    }
    
    var minimumDailyTasks: Int {
        switch self {
        case .hustle: return 3
        case .grind: return 2
        case .skills: return 1
        }
    }
    
    var weeklyTargetTasks: Int {
        switch self {
        case .hustle: return 15
        case .grind: return 5
        case .skills: return 5
        }
    }
    
    var monthlyTargetTasks: Int {
        switch self {
        case .hustle: return 60
        case .grind: return 20
        case .skills: return 20
        }
    }
}

// MARK: - Task Template Model
struct TaskTemplate: Identifiable, Codable {
    let id: String
    let title: String
    let description: String
    let category: RingCategory
    let frequency: TaskFrequency
    let estimatedTimeMinutes: Int
    let difficulty: TaskDifficulty
    let isRecurring: Bool
    let tags: [String]
    let fitnessIntegration: FitnessIntegration?
    
    init(id: String = UUID().uuidString, title: String, description: String, category: RingCategory, frequency: TaskFrequency = .daily, estimatedTimeMinutes: Int, difficulty: TaskDifficulty, isRecurring: Bool = true, tags: [String] = [], fitnessIntegration: FitnessIntegration? = nil) {
        self.id = id
        self.title = title
        self.description = description
        self.category = category
        self.frequency = frequency
        self.estimatedTimeMinutes = estimatedTimeMinutes
        self.difficulty = difficulty
        self.isRecurring = isRecurring
        self.tags = tags
        self.fitnessIntegration = fitnessIntegration
    }
}

// MARK: - Fitness Integration
struct FitnessIntegration: Codable {
    let healthKitTypeString: String
    let targetValue: Double
    let unitString: String
    
    // Non-codable computed properties for actual HealthKit types
    var healthKitType: HKQuantityTypeIdentifier? {
        return HKQuantityTypeIdentifier(rawValue: healthKitTypeString)
    }
    
    var unit: HKUnit {
        switch unitString {
        case "count": return HKUnit.count()
        case "kcal": return HKUnit.kilocalorie()
        case "min": return HKUnit.minute()
        case "m": return HKUnit.meter()
        default: return HKUnit.count()
        }
    }
    
    init(healthKitTypeString: String, targetValue: Double, unitString: String) {
        self.healthKitTypeString = healthKitTypeString
        self.targetValue = targetValue
        self.unitString = unitString
    }
    
    static let stepCount = FitnessIntegration(
        healthKitTypeString: HKQuantityTypeIdentifier.stepCount.rawValue,
        targetValue: 8000,
        unitString: "count"
    )
    
    static let activeEnergy = FitnessIntegration(
        healthKitTypeString: HKQuantityTypeIdentifier.activeEnergyBurned.rawValue,
        targetValue: 300,
        unitString: "kcal"
    )
    
    static let exerciseTime = FitnessIntegration(
        healthKitTypeString: HKQuantityTypeIdentifier.appleExerciseTime.rawValue,
        targetValue: 30,
        unitString: "min"
    )
    
    static let walkingDistance = FitnessIntegration(
        healthKitTypeString: HKQuantityTypeIdentifier.distanceWalkingRunning.rawValue,
        targetValue: 5000,
        unitString: "m"
    )
}

enum TaskDifficulty: String, CaseIterable, Codable {
    case easy = "Easy"
    case medium = "Medium"
    case hard = "Hard"
    
    var icon: String {
        switch self {
        case .easy: return "1.circle.fill"
        case .medium: return "2.circle.fill"
        case .hard: return "3.circle.fill"
        }
    }
    
    var color: String {
        switch self {
        case .easy: return "green"
        case .medium: return "orange"
        case .hard: return "red"
        }
    }
}

// MARK: - Daily Task Model
struct DailyTask: Identifiable, Codable {
    let id: String
    let templateId: String
    let title: String
    let description: String
    let category: RingCategory
    let frequency: TaskFrequency
    let estimatedTimeMinutes: Int
    let difficulty: TaskDifficulty
    let date: Date
    var status: TaskStatus
    var completedAt: Date?
    var notes: String?
    var fitnessData: FitnessData?
    
    init(from template: TaskTemplate, date: Date = Date()) {
        self.id = UUID().uuidString
        self.templateId = template.id
        self.title = template.title
        self.description = template.description
        self.category = template.category
        self.frequency = template.frequency
        self.estimatedTimeMinutes = template.estimatedTimeMinutes
        self.difficulty = template.difficulty
        self.date = date
        self.status = .pending
        self.completedAt = nil
        self.notes = nil
        self.fitnessData = nil
    }
    
    init(from template: TaskTemplate, date: Date = Date(), status: TaskStatus, completedAt: Date? = nil) {
        self.id = UUID().uuidString
        self.templateId = template.id
        self.title = template.title
        self.description = template.description
        self.category = template.category
        self.frequency = template.frequency
        self.estimatedTimeMinutes = template.estimatedTimeMinutes
        self.difficulty = template.difficulty
        self.date = date
        self.status = status
        self.completedAt = completedAt
        self.notes = nil
        self.fitnessData = nil
    }
    
    var isCompleted: Bool {
        status == .completed
    }
    
    var isOverdue: Bool {
        !isCompleted && Calendar.current.isDateInYesterday(date)
    }
    
    var isToday: Bool {
        Calendar.current.isDateInToday(date)
    }
    
    var isThisWeek: Bool {
        Calendar.current.isDate(date, equalTo: Date(), toGranularity: .weekOfYear)
    }
    
    var isThisMonth: Bool {
        Calendar.current.isDate(date, equalTo: Date(), toGranularity: .month)
    }
}

// MARK: - Fitness Data
struct FitnessData: Codable {
    let value: Double
    let unit: String
    let recordedAt: Date
    let source: String // "HealthKit", "Manual", etc.
    
    init(value: Double, unit: String, recordedAt: Date = Date(), source: String = "HealthKit") {
        self.value = value
        self.unit = unit
        self.recordedAt = recordedAt
        self.source = source
    }
}

enum TaskStatus: String, CaseIterable, Codable {
    case pending = "Pending"
    case completed = "Completed"
    case skipped = "Skipped"
    
    var icon: String {
        switch self {
        case .pending: return "circle"
        case .completed: return "checkmark.circle.fill"
        case .skipped: return "xmark.circle.fill"
        }
    }
    
    var color: String {
        switch self {
        case .pending: return "gray"
        case .completed: return "green"
        case .skipped: return "orange"
        }
    }
}

// MARK: - Progress Ring Model
struct TaskProgressRing: Identifiable {
    let id: String
    let category: RingCategory
    let progress: Double // 0.0 to 1.0
    let completedTasks: Int
    let totalTasks: Int
    let targetMet: Bool
    let frequency: TaskFrequency
    
    init(category: RingCategory, completedTasks: Int, totalTasks: Int, frequency: TaskFrequency = .daily) {
        self.id = "\(category.rawValue)_\(frequency.rawValue)"
        self.category = category
        self.completedTasks = completedTasks
        self.totalTasks = totalTasks
        self.frequency = frequency
        self.progress = totalTasks > 0 ? Double(completedTasks) / Double(totalTasks) : 0.0
        
        let target = switch frequency {
        case .daily: category.minimumDailyTasks
        case .weekly: category.weeklyTargetTasks
        case .monthly: category.monthlyTargetTasks
        case .anytime: 1
        }
        
        self.targetMet = completedTasks >= target
    }
}

// MARK: - Daily Progress Model
struct DailyProgress: Identifiable, Codable {
    let id: String
    let date: Date
    let hustleRing: Int // 0-100
    let healthRing: Int // 0-100
    let mindRing: Int   // 0-100
    let streakCount: Int
    let totalTasksCompleted: Int
    
    init(date: Date, hustleRing: Int, healthRing: Int, mindRing: Int, streakCount: Int, totalTasksCompleted: Int) {
        self.id = UUID().uuidString
        self.date = date
        self.hustleRing = hustleRing
        self.healthRing = healthRing
        self.mindRing = mindRing
        self.streakCount = streakCount
        self.totalTasksCompleted = totalTasksCompleted
    }
    
    var averageProgress: Double {
        Double(hustleRing + healthRing + mindRing) / 3.0
    }
    
    var allRingsComplete: Bool {
        hustleRing >= 100 && healthRing >= 100 && mindRing >= 100
    }
}

// MARK: - Anytime Task Categories
enum AnytimeTaskType: String, CaseIterable, Codable {
    case learn = "Learn"
    case exercise = "Exercise"
    case eatWell = "Eat Well"
    case meditate = "Meditate"
    case network = "Network"
    case skill = "Skill Building"
    
    var icon: String {
        switch self {
        case .learn: return "book.fill"
        case .exercise: return "figure.run"
        case .eatWell: return "leaf.fill"
        case .meditate: return "mindfulness"
        case .network: return "person.3.fill"
        case .skill: return "star.fill"
        }
    }
    
    var color: String {
        switch self {
        case .learn: return "blue"
        case .exercise: return "green"
        case .eatWell: return "orange"
        case .meditate: return "purple"
        case .network: return "cyan"
        case .skill: return "yellow"
        }
    }
    
    var ringCategory: RingCategory {
        switch self {
        case .learn, .skill: return .skills
        case .exercise, .eatWell: return .grind
        case .meditate: return .skills
        case .network: return .hustle
        }
    }
} 