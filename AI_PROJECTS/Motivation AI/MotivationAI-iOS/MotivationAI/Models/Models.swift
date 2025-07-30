import Foundation
import SwiftUI

// MARK: - User Model
struct User: Identifiable {
    let id: String
    let name: String
    let email: String
    let plan: SubscriptionPlan
}

enum SubscriptionPlan: String, CaseIterable {
    case free = "Free"
    case premium = "Premium"
    case expert = "Expert"
}

// MARK: - Legacy Task Models (moved to TaskModels.swift)
// Old task models have been replaced by comprehensive TaskModels.swift

// MARK: - Enhanced Message System
struct MotivationalMessage: Identifiable, Codable {
    let id: String
    let title: String
    let content: String
    let author: String?
    let category: MessageCategory
    let timeOfDay: TimeOfDay
    let tone: MessageTone
    let backgroundImageName: String?
    let audioEnabled: Bool
    let duration: Int // seconds for display
    let actionPrompt: String? // Optional call-to-action
    
    // Computed properties
    var shortContent: String {
        String(content.prefix(100)) + (content.count > 100 ? "..." : "")
    }
    
    var isScheduled: Bool {
        timeOfDay != .anytime
    }
}

// Legacy support for existing DailyMessage usage
typealias DailyMessage = MotivationalMessage

enum MessageCategory: String, CaseIterable, Codable {
    case morningWakeUp = "Morning Wake-Up"
    case midDayCheckIn = "Mid-Day Check-In"
    case eveningWindDown = "Evening Wind-Down"
    case taskCelebration = "Task Celebration"
    case linkedInFocus = "LinkedIn Focus"
    case generalMotivation = "General Motivation"
    case toughLove = "Tough Love"
    case weekendBoost = "Weekend Boost"
    case actionOriented = "Action-Oriented"
    case compassionate = "Compassionate"
    case interviewPrep = "Interview Prep"
    case rejectionRecovery = "Rejection Recovery"
    case networkBuilding = "Network Building"
    case fridayMotivation = "Friday Motivation"
    case mondayEnergy = "Monday Energy"
    case specialCircumstances = "Special Circumstances"
    
    var icon: String {
        switch self {
        case .morningWakeUp: return "sunrise.fill"
        case .midDayCheckIn: return "sun.max.fill"
        case .eveningWindDown: return "sunset.fill"
        case .taskCelebration: return "party.popper.fill"
        case .linkedInFocus: return "link"
        case .generalMotivation: return "flame.fill"
        case .toughLove: return "bolt.fill"
        case .weekendBoost: return "gamecontroller.fill"
        case .actionOriented: return "forward.fill"
        case .compassionate: return "heart.fill"
        case .interviewPrep: return "person.crop.rectangle.stack.fill"
        case .rejectionRecovery: return "arrow.up.circle.fill"
        case .networkBuilding: return "person.3.fill"
        case .fridayMotivation: return "star.fill"
        case .mondayEnergy: return "bolt.circle.fill"
        case .specialCircumstances: return "sparkles"
        }
    }
    
    var color: String {
        switch self {
        case .morningWakeUp: return "orange"
        case .midDayCheckIn: return "blue"
        case .eveningWindDown: return "purple"
        case .taskCelebration: return "green"
        case .linkedInFocus: return "blue"
        case .generalMotivation: return "red"
        case .toughLove: return "red"
        case .weekendBoost: return "cyan"
        case .actionOriented: return "orange"
        case .compassionate: return "pink"
        case .interviewPrep: return "indigo"
        case .rejectionRecovery: return "green"
        case .networkBuilding: return "blue"
        case .fridayMotivation: return "yellow"
        case .mondayEnergy: return "red"
        case .specialCircumstances: return "purple"
        }
    }
}

enum TimeOfDay: String, CaseIterable, Codable {
    case morning = "Morning" // 6-11 AM
    case midday = "Midday"   // 11 AM - 2 PM
    case afternoon = "Afternoon" // 2-6 PM
    case evening = "Evening" // 6-10 PM
    case night = "Night"     // 10 PM - 6 AM
    case anytime = "Anytime"
    
    var scheduledHour: Int? {
        switch self {
        case .morning: return 7
        case .midday: return 12
        case .afternoon: return 15
        case .evening: return 18
        case .night: return 21
        case .anytime: return nil
        }
    }
    
    var timeRange: String {
        switch self {
        case .morning: return "6:00 AM - 11:00 AM"
        case .midday: return "11:00 AM - 2:00 PM"
        case .afternoon: return "2:00 PM - 6:00 PM"
        case .evening: return "6:00 PM - 10:00 PM"
        case .night: return "10:00 PM - 6:00 AM"
        case .anytime: return "Any Time"
        }
    }
}

enum MessageTone: String, CaseIterable, Codable {
    case energetic = "Energetic"
    case compassionate = "Compassionate"
    case toughLove = "Tough Love"
    case professional = "Professional"
    case playful = "Playful"
    case inspiring = "Inspiring"
    case actionFocused = "Action-Focused"
    
    var description: String {
        switch self {
        case .energetic: return "High-energy, motivating tone"
        case .compassionate: return "Gentle, understanding tone"
        case .toughLove: return "Direct, no-nonsense approach"
        case .professional: return "Business-focused, strategic"
        case .playful: return "Fun, lighthearted motivation"
        case .inspiring: return "Uplifting, aspirational"
        case .actionFocused: return "Task-oriented, immediate action"
        }
    }
}

// MARK: - Learning Path Model
struct LearningPath: Identifiable {
    let id: String
    let title: String
    let description: String
    let category: LearningCategory
    var progress: Double = 0.0
    var lessons: [Lesson] = []
}

struct Lesson: Identifiable, Codable {
    let id: String
    let title: String
    let duration: String
    let content: String
    var isCompleted: Bool
    let order: Int
    
    init(id: String = UUID().uuidString, title: String, duration: String, content: String, isCompleted: Bool = false, order: Int) {
        self.id = id
        self.title = title
        self.duration = duration
        self.content = content
        self.isCompleted = isCompleted
        self.order = order
    }
}

enum LearningCategory: String, CaseIterable {
    case jobSearch = "Job Search"
    case interview = "Interview"
    case skills = "Skills"
    case networking = "Networking"
    
    var icon: String {
        switch self {
        case .jobSearch: return "magnifyingglass"
        case .interview: return "mic.fill"
        case .skills: return "star.fill"
        case .networking: return "person.3.fill"
        }
    }
}

// MARK: - User Progress Model
struct UserProgress: Identifiable {
    let id: String = UUID().uuidString
    let userId: String
    var level: Int
    var experiencePoints: Int
    var tasksCompleted: Int
    var streakDays: Int
    var achievements: [String]
    
    // Computed properties for progress tracking
    var experiencePointsToNextLevel: Int {
        let baseXP = 100
        let nextLevelXP = baseXP * level * 2
        return max(0, nextLevelXP - experiencePoints)
    }
    
    var progressToNextLevel: Double {
        let baseXP = 100
        let currentLevelXP = baseXP * (level - 1) * 2
        let nextLevelXP = baseXP * level * 2
        let levelRange = nextLevelXP - currentLevelXP
        let currentProgress = experiencePoints - currentLevelXP
        return min(1.0, max(0.0, Double(currentProgress) / Double(levelRange)))
    }
    
    var levelTitle: String {
        switch level {
        case 1: return "Job Seeker"
        case 2: return "Applicant"
        case 3: return "Networker"
        case 4: return "Interview Pro"
        case 5: return "Career Champion"
        case 6...10: return "Job Hunter Elite"
        case 11...20: return "Career Master"
        default: return "Career Legend"
        }
    }
} 

// MARK: - Profile & Settings Models
struct UserProfile: Codable {
    var personalInfo: PersonalInfo
    var preferences: UserPreferences
    var careerInfo: CareerInfo
    var goals: [Goal]
    var notifications: NotificationSettings
    
    init() {
        self.personalInfo = PersonalInfo()
        self.preferences = UserPreferences()
        self.careerInfo = CareerInfo()
        self.goals = []
        self.notifications = NotificationSettings()
    }
}

struct PersonalInfo: Codable {
    var name: String = ""
    var age: Int = 25
    var yearsOfExperience: Int = 0
    var industry: String = ""
    var currentJobTitle: String = ""
    var location: String = ""
    var profileImageName: String? = nil
}

struct UserPreferences: Codable {
    var theme: AppTheme = .dark
    var coachingStyle: CoachingStyle = .coach
    var taskIntensity: TaskIntensity = .moderate
    var weekendMode: Bool = false
    var motivationLevel: MotivationLevel = .balanced
}

struct CareerInfo: Codable {
    var previousJob: JobInfo?
    var targetJob: JobInfo?
    var jobSearchStatus: JobSearchStatus = .exploring
    var linkedInProfile: String = ""
    var portfolioURL: String = ""
    var resume: String = ""
}

struct JobInfo: Codable {
    var title: String = ""
    var company: String = ""
    var duration: String = ""
    var description: String = ""
    var salary: String = ""
}

struct Goal: Identifiable, Codable {
    let id = UUID()
    var title: String
    var description: String
    var category: GoalCategory
    var targetDate: Date?
    var isCompleted: Bool = false
    var priority: GoalPriority
    
    enum CodingKeys: String, CodingKey {
        case title, description, category, targetDate, isCompleted, priority
    }
}

struct NotificationSettings: Codable {
    var wakeUpTime: Date = Calendar.current.date(from: DateComponents(hour: 7, minute: 0)) ?? Date()
    var midDayCheckIn: Date = Calendar.current.date(from: DateComponents(hour: 12, minute: 0)) ?? Date()
    var afternoonWrap: Date = Calendar.current.date(from: DateComponents(hour: 17, minute: 0)) ?? Date()
    var goodnightTime: Date = Calendar.current.date(from: DateComponents(hour: 21, minute: 0)) ?? Date()
    var enableNotifications: Bool = true
    var weekendNotifications: Bool = false
    var motivationalMessages: Bool = true
}

// MARK: - Profile Enums
enum AppTheme: String, CaseIterable, Codable {
    case light = "Light"
    case dark = "Dark"
    case chill = "Chill"
    case warm = "Warm"
    
    var colors: (primary: Color, secondary: Color, background: Color) {
        switch self {
        case .light:
            return (.black, .gray, .white)
        case .dark:
            return (.white, .gray, Color(red: 0, green: 0, blue: 0))
        case .chill:
            return (.cyan, .blue, Color(red: 0.05, green: 0.1, blue: 0.15))
        case .warm:
            return (.orange, .red, Color(red: 0.15, green: 0.1, blue: 0.05))
        }
    }
}

enum CoachingStyle: String, CaseIterable, Codable {
    case chill = "Chill"
    case counselor = "Counselor"
    case coach = "Coach"
    case drillSergeant = "Drill Sergeant"
    
    var description: String {
        switch self {
        case .chill:
            return "Relaxed, supportive approach"
        case .counselor:
            return "Empathetic, understanding guidance"
        case .coach:
            return "Balanced motivation and accountability"
        case .drillSergeant:
            return "Direct, intense, no-nonsense push"
        }
    }
    
    var icon: String {
        switch self {
        case .chill: return "leaf.fill"
        case .counselor: return "heart.fill"
        case .coach: return "figure.coaching"
        case .drillSergeant: return "bolt.fill"
        }
    }
}

enum TaskIntensity: String, CaseIterable, Codable {
    case light = "Light Load"
    case moderate = "Moderate"
    case heavy = "Heavy Load"
    case maximum = "Maximum"
    
    var description: String {
        switch self {
        case .light:
            return "2-3 tasks per day, gentle pace"
        case .moderate:
            return "4-6 tasks per day, steady progress"
        case .heavy:
            return "7-10 tasks per day, focused hustle"
        case .maximum:
            return "10+ tasks per day, all-out grind"
        }
    }
    
    var taskCount: Int {
        switch self {
        case .light: return 3
        case .moderate: return 6
        case .heavy: return 10
        case .maximum: return 15
        }
    }
}

enum MotivationLevel: String, CaseIterable, Codable {
    case gentle = "Gentle"
    case balanced = "Balanced"
    case intense = "Intense"
    case extreme = "Extreme"
}

enum JobSearchStatus: String, CaseIterable, Codable {
    case employed = "Currently Employed"
    case exploring = "Exploring Options"
    case activelySearching = "Actively Searching"
    case interviewing = "In Interview Process"
    case negotiating = "Negotiating Offers"
    case transitioning = "Between Roles"
}

enum GoalCategory: String, CaseIterable, Codable {
    case career = "Career"
    case skill = "Skill Development"
    case networking = "Networking"
    case personal = "Personal"
    case financial = "Financial"
    case health = "Health & Wellness"
}

enum GoalPriority: String, CaseIterable, Codable {
    case low = "Low"
    case medium = "Medium"
    case high = "High"
    case critical = "Critical"
    
    var color: Color {
        switch self {
        case .low: return .green
        case .medium: return .yellow
        case .high: return .orange
        case .critical: return .red
        }
    }
}

// MARK: - Profile Data Manager
class ProfileManager: ObservableObject {
    @Published var userProfile: UserProfile
    
    private let userDefaults = UserDefaults.standard
    private let profileKey = "user_profile"
    
    init() {
        if let data = userDefaults.data(forKey: profileKey),
           let profile = try? JSONDecoder().decode(UserProfile.self, from: data) {
            self.userProfile = profile
        } else {
            self.userProfile = UserProfile()
        }
    }
    
    func saveProfile() {
        if let data = try? JSONEncoder().encode(userProfile) {
            userDefaults.set(data, forKey: profileKey)
        }
    }
    
    func updatePersonalInfo(_ info: PersonalInfo) {
        userProfile.personalInfo = info
        saveProfile()
    }
    
    func updatePreferences(_ preferences: UserPreferences) {
        userProfile.preferences = preferences
        saveProfile()
    }
    
    func updateCareerInfo(_ careerInfo: CareerInfo) {
        userProfile.careerInfo = careerInfo
        saveProfile()
    }
    
    func addGoal(_ goal: Goal) {
        userProfile.goals.append(goal)
        saveProfile()
    }
    
    func updateGoal(_ goal: Goal) {
        if let index = userProfile.goals.firstIndex(where: { $0.id == goal.id }) {
            userProfile.goals[index] = goal
            saveProfile()
        }
    }
    
    func deleteGoal(_ goal: Goal) {
        userProfile.goals.removeAll { $0.id == goal.id }
        saveProfile()
    }
    
    func updateNotificationSettings(_ settings: NotificationSettings) {
        userProfile.notifications = settings
        saveProfile()
    }
    
    // MARK: - Learning Progress Methods
    func getTotalCompletedLessons() -> Int {
        var totalCompleted = 0
        
        for course in CourseDataProvider.shared.allCourses {
            let key = "completed_lessons_\(course.id)"
            if let data = UserDefaults.standard.data(forKey: key),
               let lessons = try? JSONDecoder().decode(Set<String>.self, from: data) {
                totalCompleted += lessons.count
            }
        }
        
        return totalCompleted
    }
    
    func getTotalAvailableLessons() -> Int {
        return CourseDataProvider.shared.allCourses.reduce(0) { total, course in
            total + course.lessons.count
        }
    }
    
    func getCompletedCoursesCount() -> Int {
        var completedCourses = 0
        
        for course in CourseDataProvider.shared.allCourses {
            let key = "completed_lessons_\(course.id)"
            if let data = UserDefaults.standard.data(forKey: key),
               let completedLessons = try? JSONDecoder().decode(Set<String>.self, from: data) {
                if completedLessons.count == course.lessons.count {
                    completedCourses += 1
                }
            }
        }
        
        return completedCourses
    }
    
    func getLearningProgressPercentage() -> Int {
        let total = getTotalAvailableLessons()
        guard total > 0 else { return 0 }
        
        let completed = getTotalCompletedLessons()
        return Int((Double(completed) / Double(total)) * 100)
    }
    
    func getRecommendedAction() -> (title: String, subtitle: String, count: Int, color: Color) {
        let completedLessons = getTotalCompletedLessons()
        let coachingStyle = userProfile.preferences.coachingStyle
        
        if completedLessons == 0 {
            switch coachingStyle {
            case .chill:
                return ("Start Learning", "Begin your journey", 5, .blue)
            case .counselor:
                return ("Learn & Grow", "Take the first step", 5, .green)
            case .coach:
                return ("Skill Building", "Level up today", 5, .purple)
            case .drillSergeant:
                return ("Train Hard", "No excuses", 5, .red)
            }
        } else if completedLessons < 10 {
            switch coachingStyle {
            case .chill:
                return ("Continue Learning", "Keep flowing", completedLessons, .blue)
            case .counselor:
                return ("Great Progress", "You're doing well", completedLessons, .green)
            case .coach:
                return ("Momentum Building", "Keep pushing", completedLessons, .purple)
            case .drillSergeant:
                return ("Stay Focused", "Don't stop now", completedLessons, .red)
            }
        } else {
            switch coachingStyle {
            case .chill:
                return ("Learning Flow", "In the zone", completedLessons, .cyan)
            case .counselor:
                return ("Excellent Work", "So proud of you", completedLessons, .green)
            case .coach:
                return ("Skill Master", "Crushing it", completedLessons, .purple)
            case .drillSergeant:
                return ("Dominating", "Unstoppable", completedLessons, .orange)
            }
        }
    }
    
    func notifyLessonCompleted() {
        // This method is called when a lesson is completed to trigger UI updates
        // The @Published userProfile will automatically notify observers
        objectWillChange.send()
    }
} 

// MARK: - Missing Models for AppViewModel
struct JobApplication: Identifiable, Codable {
    let id: String
    let companyName: String
    let position: String
    let status: ApplicationStatus
    let dateApplied: Date
    let notes: String?
}

enum ApplicationStatus: String, CaseIterable, Codable {
    case applied = "Applied"
    case interviewing = "Interviewing"
    case offered = "Offered"
    case rejected = "Rejected"
}

// DailyTask moved to TaskModels.swift

struct Achievement: Identifiable, Codable {
    let id: String
    let title: String
    let description: String
    let earnedDate: Date
    let icon: String
}

struct EmergencyContact: Identifiable, Codable {
    let id: String
    let name: String
    let relationship: String
    let phoneNumber: String
    let email: String?
}

struct TherapistInfo: Codable {
    let name: String
    let phoneNumber: String
    let email: String?
    let nextAppointment: Date?
    let emergencyNumber: String?
}

struct MoodEntry: Identifiable, Codable {
    let id: String
    let mood: MoodLevel
    let date: Date
    let notes: String?
}

enum MoodLevel: String, CaseIterable, Codable {
    case excellent = "Excellent"
    case good = "Good"
    case okay = "Okay"
    case struggling = "Struggling"
    case difficult = "Difficult"
} 

// MARK: - Course Learning System
struct Course: Identifiable, Codable {
    let id: String
    let title: String
    let description: String
    let duration: String
    let difficulty: CourseDifficulty
    let category: CourseCategory
    let type: CourseType
    let price: Double?
    let lessons: [Lesson]
    let tags: [String]
    let instructor: String
    let thumbnailColor: CourseColor
    let completionPercentage: Double
    let isCompleted: Bool
    
    init(id: String = UUID().uuidString, title: String, description: String, duration: String, difficulty: CourseDifficulty, category: CourseCategory, type: CourseType, price: Double? = nil, lessons: [Lesson] = [], tags: [String] = [], instructor: String = "Rise & Grind Team", thumbnailColor: CourseColor, completionPercentage: Double = 0.0, isCompleted: Bool = false) {
        self.id = id
        self.title = title
        self.description = description
        self.duration = duration
        self.difficulty = difficulty
        self.category = category
        self.type = type
        self.price = price
        self.lessons = lessons
        self.tags = tags
        self.instructor = instructor
        self.thumbnailColor = thumbnailColor
        self.completionPercentage = completionPercentage
        self.isCompleted = isCompleted
    }
}

enum CourseDifficulty: String, CaseIterable, Codable {
    case beginner = "Beginner"
    case intermediate = "Intermediate"
    case advanced = "Advanced"
    
    var color: CourseColor {
        switch self {
        case .beginner: return .green
        case .intermediate: return .orange
        case .advanced: return .red
        }
    }
}

enum CourseCategory: String, CaseIterable, Codable {
    case jobSearch = "Job Search"
    case interviewing = "Interviewing"
    case networking = "Networking"
    case resumeCV = "Resume & CV"
    case aiTools = "AI Tools"
    case careerDevelopment = "Career Development"
    case softSkills = "Soft Skills"
    case techSkills = "Tech Skills"
    
    var icon: String {
        switch self {
        case .jobSearch: return "magnifyingglass"
        case .interviewing: return "person.2"
        case .networking: return "link"
        case .resumeCV: return "doc.text"
        case .aiTools: return "brain.head.profile"
        case .careerDevelopment: return "chart.line.uptrend.xyaxis"
        case .softSkills: return "heart"
        case .techSkills: return "laptopcomputer"
        }
    }
}

enum CourseType: String, CaseIterable, Codable {
    case free = "Free"
    case premium = "Premium"
    case subscription = "Subscription"
    
    var displayText: String {
        switch self {
        case .free: return "Free"
        case .premium: return "Premium"
        case .subscription: return "Pro"
        }
    }
    
    var color: CourseColor {
        switch self {
        case .free: return .green
        case .premium: return .orange
        case .subscription: return .purple
        }
    }
}

enum CourseColor: String, CaseIterable, Codable {
    case orange, blue, green, red, purple, cyan, yellow, indigo
    
    var swiftUIColor: Color {
        switch self {
        case .orange: return .orange
        case .blue: return .blue
        case .green: return .green
        case .red: return .red
        case .purple: return .purple
        case .cyan: return .cyan
        case .yellow: return .yellow
        case .indigo: return .indigo
        }
    }
}

class CourseDataProvider {
    static let shared = CourseDataProvider()
    
    private init() {}
    
    // MARK: - Free Courses (First 5)
    lazy var freeCourses: [Course] = [
        Course(
            title: "Job Search Fundamentals",
            description: "Strategic job search approach for experienced professionals. Navigate career transitions with confidence, leverage your experience effectively, and position yourself competitively in today's market.",
            duration: "4h 15m",
            difficulty: .intermediate,
            category: .jobSearch,
            type: .free,
            lessons: [
                Lesson(title: "Strategic Positioning During Transition", duration: "15m", content: """
# Strategic Positioning During Transition

## The Executive Mindset Shift

When you're between roles, the narrative you control determines everything. Most executives make the critical error of approaching transition defensively—explaining gaps, justifying decisions, minimizing impact. This is amateur hour.

**The Professional Reality:**
• 67% of C-suite executives experience at least one "unexpected" transition
• Top performers average 3.2 executive-level transitions in their career
• 89% of board-level appointments come from candidates who positioned their transition as strategic

---

## The PIVOT Framework™

### **P** - Position as Intentional
Transform "I was laid off" into "I leveraged the restructuring to pursue my next strategic challenge."

**Script Example:**
❌ "Unfortunately, the company eliminated my position during downsizing."
✅ "The acquisition created an ideal inflection point for me to pursue the transformation leadership role I'd been targeting."

### **I** - Illustrate Value Created
Every transition should highlight the value you delivered before moving.

**The Value Bridge:**
```
Previous Role Achievement → Market Recognition → Strategic Opportunity
```
"Leading the digital transformation that increased EBITDA by $47M positioned me perfectly for this Chief Digital Officer search."

### **V** - Validate Through Timing
Position timing as strategic advantage, not circumstance.

**Timing Narratives:**
• "Market Optimization" - You're moving at the perfect industry moment
• "Portfolio Expansion" - Adding complementary expertise to your leadership portfolio  
• "Platform Building" - Creating the foundation for your next level of impact

### **O** - Opportunity Lens
Frame every conversation around opportunity, never necessity.

**Language Architecture:**
- "Exploring opportunities that leverage my..." (not "Looking for a job because...")
- "Evaluating platforms where I can..." (not "Need a position that...")
- "Considering challenges that require..." (not "Hoping to find...")

### **T** - Timeline Mastery
Control the urgency narrative completely.

**The Executive Timeline:**
```
Phase 1: Strategic Assessment (2-3 months)
Phase 2: Market Evaluation (2-4 months)  
Phase 3: Opportunity Curation (1-3 months)
```

---

## Implementation Checklist

□ Craft your PIVOT positioning for each conversation context
□ Develop 3 different timeline narratives based on audience
□ Practice the 30-second positioning statement until unconscious
□ Prepare value bridge stories for each major achievement
□ Create advisory/consulting narrative for extended timelines

**Next Lesson Preview:** Executive Network Activation - How to leverage C-suite relationships to access hidden opportunities and board-level introductions.
""", order: 1),
                Lesson(title: "Executive Network Activation", duration: "20m", content: """
# Executive Network Activation

## The Hidden Executive Market Reality

**Critical Intel:**
• 78% of C-suite roles are filled before public posting
• 92% of board appointments come through direct relationship introductions  
• Executive search firms fill 67% of positions through their network before external search
• The "hidden market" represents $2.8B in annual executive compensation

**Translation:** If you're applying online, you're already losing.

---

## The Executive Network Pyramid

```
                    📊 BOARD LEVEL
                   /              \\
              🤝 C-SUITE    💼 SEARCH CONSULTANTS
             /        \\              /
    🏛️ INDUSTRY    🎯 FUNCTIONAL    🌐 ALUMNI
   LEADERS        SPECIALISTS     NETWORKS
```

### **Level 1: Board Connections**
**Target:** Current and former board members in your industry/function
**Approach:** Strategic value positioning, not job seeking
**Conversation:** "I'm evaluating the market and would value your perspective on..."

### **Level 2: C-Suite Peers**
**Target:** CEOs, COOs, CTOs who understand your level
**Approach:** Peer-to-peer market intelligence sharing
**Conversation:** "I'm seeing interesting trends in [domain] and wondered if you're experiencing..."

### **Level 3: Executive Search Consultants**
**Target:** Partners at Korn Ferry, Russell Reynolds, Spencer Stuart, Heidrick & Struggles
**Approach:** Relationship building, not immediate placement
**Conversation:** "I'm not actively searching, but wanted to connect given my experience in..."

---

## Network Activation Playbook

### **Week 1-2: Audit & Map**
□ Complete executive network audit using pyramid structure
□ Identify top 20 strategic relationships for activation
□ Research recent developments/challenges for each contact
□ Prepare market intelligence value propositions

### **Week 3-4: Reactivation Campaign**
□ Send 5 "market intelligence" outreach messages per week
□ Schedule 3-5 executive conversations weekly
□ Prepare industry insight summaries to share
□ Document intelligence gathered for future conversations

### **Week 5-8: Strategic Positioning**
□ Transition conversations to strategic advice seeking
□ Request introductions based on value provided
□ Position for "passive candidate" consideration
□ Maintain advisory-level relationship cadence

**Next Lesson Preview:** Compensation Negotiation from Transition - How to negotiate from strength even when unemployed, including research tactics and total compensation optimization.
""", order: 2),
                Lesson(title: "Compensation Negotiation from Transition", duration: "25m", content: """
# Compensation Negotiation from Transition

## The Executive Compensation Reality Check

**Market Intelligence:**
• C-suite executives in transition often command 15-30% salary increases
• 73% of executives accept first offers due to transition anxiety
• Top performers leverage transition timing for total compensation optimization
• Executive search firm placements average 27% higher compensation than direct applications

**The Transition Advantage:**
You're evaluating multiple opportunities, not desperately seeking one.

---

## The Executive Compensation Research Architecture

### **Layer 1: Market Intelligence**
**Primary Sources:**
• Compensation consultants (Pearl Meyer, Aon, Willis Towers Watson)
• Executive search consultant intelligence
• Public company proxy statements (Schedule DEF 14A)
• Private equity portfolio company benchmarks

**Research Framework:**
```
Base Salary + Annual Bonus + Equity Value + Benefits + Perquisites = Total Compensation
```

### **Layer 2: Industry Benchmarking**
**The Compensation Comparison Matrix:**

| **Component** | **Your Target** | **Market 25th %** | **Market Median** | **Market 75th %** |
|---------------|----------------|-------------------|-------------------|-------------------|
| Base Salary | $[Target] | $[Research] | $[Research] | $[Research] |
| Target Bonus | [%] of base | [%] of base | [%] of base | [%] of base |
| Equity Value | $[Annual] | $[Research] | $[Research] | $[Research] |
| Total Comp | $[Target] | $[Research] | $[Research] | $[Research] |

---

## The Transition Negotiation Strategy

### **Phase 1: Establish Value Before Price**
**Never discuss compensation until you've established irreplaceable value.**

**Value Establishment Framework:**
```
Business Challenge → Your Solution → Quantified Impact → Compensation Discussion
```

### **Phase 2: The Transition Timeline Leverage**
**Use your strategic timeline as negotiation advantage.**

**Positioning:**
"I'm evaluating several opportunities simultaneously, and while [Company] is my preferred platform, I need to understand how the total compensation package positions against other considerations."

### **Phase 3: Total Compensation Optimization**
**Negotiate the package, not just the salary.**

---

## Implementation Checklist

□ Complete comprehensive compensation research using all three layers
□ Develop value proposition narrative before compensation discussion
□ Prepare market intelligence data for negotiation
□ Structure negotiation approach based on offer scenario
□ Plan total compensation optimization strategy beyond base salary

**Next Lesson Preview:** Cross-Industry Experience Translation - How to position your expertise for new industries and overcome hiring bias through strategic narrative construction.
""", order: 3)
            ],
            tags: ["executive search", "career transition", "leadership", "strategy"],
            thumbnailColor: .blue,
            completionPercentage: 0.0
        ),
        
        Course(
            title: "How to Use AI to Find That Job",
            description: "Leverage artificial intelligence tools to supercharge your job search. From AI-powered resume optimization to interview prep, learn how to use technology to your advantage.",
            duration: "3h 15m",
            difficulty: .intermediate,
            category: .aiTools,
            type: .free,
            lessons: [
                Lesson(title: "AI Tools Overview for Job Seekers", duration: "20m", content: "Introduction to AI-powered job search tools", order: 1),
                Lesson(title: "AI Resume Optimization", duration: "35m", content: "Use AI to tailor resumes for ATS systems", order: 2),
                Lesson(title: "ChatGPT for Cover Letters", duration: "30m", content: "Craft compelling cover letters with AI assistance", order: 3),
                Lesson(title: "AI-Powered Job Matching", duration: "25m", content: "Find relevant opportunities using AI platforms", order: 4),
                Lesson(title: "Interview Prep with AI", duration: "40m", content: "Practice interviews and get AI feedback", order: 5),
                Lesson(title: "LinkedIn Optimization with AI", duration: "25m", content: "Enhance your profile using AI writing tools", order: 6)
            ],
            tags: ["AI", "technology", "automation", "efficiency"],
            thumbnailColor: .purple,
            completionPercentage: 0.0
        ),
        
        Course(
            title: "Resume Writing Mastery",
            description: "Executive-level resume strategy for senior professionals. Position complex career narratives, quantify leadership impact, and create documents that open C-suite conversations.",
            duration: "3h 30m",
            difficulty: .intermediate,
            category: .resumeCV,
            type: .free,
            lessons: [
                Lesson(title: "Executive Resume Architecture", duration: "35m", content: "Strategic document structure for senior roles. Lead with impact, organize by value delivered, and create executive presence on paper.", order: 1),
                Lesson(title: "Quantifying Leadership Impact", duration: "45m", content: "Transform soft leadership accomplishments into hard metrics. Revenue growth, team scaling, operational efficiency, and stakeholder management results.", order: 2),
                Lesson(title: "Career Narrative Cohesion", duration: "40m", content: "Connect career moves into a compelling progression story. Address industry switches, title variations, and complex reporting structures for senior roles.", order: 3),
                Lesson(title: "Board-Ready Professional Summary", duration: "30m", content: "Write executive summaries that position you for board consideration. Industry expertise, transformation leadership, and strategic value proposition.", order: 4),
                Lesson(title: "Executive Reference Integration", duration: "25m", content: "Subtly incorporate high-level endorsements and board relationships. Name-dropping with purpose and positioning peer-level references.", order: 5),
                Lesson(title: "Multi-Format Resume Strategy", duration: "35m", content: "Adapt your executive story for different contexts: executive search firms, board applications, speaking engagements, and direct approaches.", order: 6)
            ],
            tags: ["executive resume", "leadership", "C-suite", "board ready"],
            thumbnailColor: .green,
            completionPercentage: 0.0
        ),
        
        Course(
            title: "Interview Confidence Builder",
            description: "Executive interview mastery for senior professionals. Navigate board presentations, CEO conversations, and multi-stakeholder evaluation processes with commanding presence.",
            duration: "5h 20m",
            difficulty: .advanced,
            category: .interviewing,
            type: .free,
            lessons: [
                Lesson(title: "Executive Interview Landscape", duration: "35m", content: "Navigate complex interview processes: search firms, board interviews, peer conversations, and cultural fit assessments unique to senior roles.", order: 1),
                Lesson(title: "Strategic Case Study Mastery", duration: "55m", content: "Handle complex business scenarios and transformation challenges. Present strategic thinking, risk assessment, and implementation roadmaps under pressure.", order: 2),
                Lesson(title: "Board Presentation Skills", duration: "50m", content: "Present to board-level audiences with confidence. Handle challenging questions from investors, independent directors, and activist shareholders.", order: 3),
                Lesson(title: "Crisis Leadership Scenarios", duration: "45m", content: "Demonstrate leadership during hypothetical crises. Show decision-making under uncertainty, stakeholder management, and crisis communication skills.", order: 4),
                Lesson(title: "Cultural Transformation Questions", duration: "40m", content: "Address complex organizational culture questions. Show experience in change management, team building, and cultural alignment across diverse organizations.", order: 5),
                Lesson(title: "Compensation Philosophy Discussion", duration: "30m", content: "Navigate sophisticated compensation discussions beyond salary. Equity structures, golden parachutes, performance metrics, and long-term incentive alignment.", order: 6),
                Lesson(title: "Reference Check Preparation", duration: "25m", content: "Prepare your references for executive-level due diligence. Coach former colleagues, board members, and CEO references for detailed conversations.", order: 7),
                Lesson(title: "Final Round Negotiation Strategy", duration: "40m", content: "Handle final negotiations with confidence. Total compensation packages, start dates, onboarding support, and success metrics for executive roles.", order: 8)
            ],
            tags: ["executive interview", "board presentation", "leadership assessment", "C-suite"],
            thumbnailColor: .orange,
            completionPercentage: 0.0
        ),
        
        Course(
            title: "LinkedIn Networking Power",
            description: "Executive networking mastery for senior professionals. Build C-suite connections, establish thought leadership, and access board opportunities through strategic LinkedIn presence.",
            duration: "4h 25m",
            difficulty: .advanced,
            category: .networking,
            type: .free,
            lessons: [
                Lesson(title: "Executive Personal Brand Architecture", duration: "45m", content: "Build a LinkedIn presence that attracts board opportunities and C-suite conversations. Position expertise, showcase thought leadership, and create executive magnetism.", order: 1),
                Lesson(title: "C-Suite Connection Strategy", duration: "50m", content: "Connect with CEOs, board members, and industry leaders strategically. Navigate gatekeepers, provide value before asking, and build relationships at the executive level.", order: 2),
                Lesson(title: "Thought Leadership Content Creation", duration: "55m", content: "Create content that positions you as an industry expert. Share strategic insights, comment on market trends, and engage in executive-level conversations.", order: 3),
                Lesson(title: "Board Network Development", duration: "40m", content: "Build relationships with current and former board members. Understand board dynamics, identify board-ready peers, and position yourself for board consideration.", order: 4),
                Lesson(title: "Industry Event Networking", duration: "35m", content: "Leverage LinkedIn for high-value industry events. Pre-event networking, strategic meeting scheduling, and post-event relationship nurturing for maximum impact.", order: 5),
                Lesson(title: "Executive Search Firm Relationships", duration: "30m", content: "Build and maintain relationships with top executive search consultants. Understand their sourcing methods, stay visible for future searches, and maintain long-term connections.", order: 6),
                Lesson(title: "Crisis Communication Leadership", duration: "25m", content: "Navigate LinkedIn during organizational crises or transitions. Maintain professional reputation, communicate with stakeholders, and lead with transparency during difficult periods.", order: 7),
                Lesson(title: "International Executive Networking", duration: "25m", content: "Build global networks for international opportunities. Navigate cultural differences, time zones, and international business etiquette in digital networking.", order: 8)
            ],
            tags: ["executive networking", "thought leadership", "C-suite connections", "board development"],
            thumbnailColor: .cyan,
            completionPercentage: 0.0
        )
    ]
    
    // MARK: - Premium Courses
    lazy var premiumCourses: [Course] = [
        Course(
            title: "Advanced Salary Negotiation",
            description: "Master the psychology and tactics of salary negotiation. Learn to research market rates, time your asks, and negotiate total compensation packages.",
            duration: "5h 30m",
            difficulty: .advanced,
            category: .careerDevelopment,
            type: .premium,
            price: 49.99,
            tags: ["salary", "negotiation", "compensation"],
            thumbnailColor: .red
        ),
        
        Course(
            title: "Executive Presence & Leadership",
            description: "Develop the presence and communication skills of top executives. Learn to command respect, influence decisions, and lead with confidence.",
            duration: "6h 15m",
            difficulty: .advanced,
            category: .softSkills,
            type: .subscription,
            tags: ["leadership", "executive", "presence"],
            thumbnailColor: .indigo
        ),
        
        Course(
            title: "Tech Industry Interview Prep",
            description: "Specialized preparation for technical roles. Coding challenges, system design, and tech-specific behavioral questions.",
            duration: "8h 45m",
            difficulty: .advanced,
            category: .techSkills,
            type: .premium,
            price: 79.99,
            tags: ["tech", "coding", "system design"],
            thumbnailColor: .blue
        ),
        
        Course(
            title: "Career Pivot Masterclass",
            description: "Successfully transition to a new industry or role. Strategic planning, skill mapping, and overcoming career change challenges.",
            duration: "7h 20m",
            difficulty: .intermediate,
            category: .careerDevelopment,
            type: .subscription,
            tags: ["career change", "pivot", "transition"],
            thumbnailColor: .purple
        ),
        
        Course(
            title: "Remote Work Excellence",
            description: "Thrive in remote and hybrid work environments. Master virtual collaboration, time management, and building remote relationships.",
            duration: "4h 45m",
            difficulty: .intermediate,
            category: .softSkills,
            type: .premium,
            price: 39.99,
            tags: ["remote work", "virtual", "collaboration"],
            thumbnailColor: .green
        ),
        
        Course(
            title: "Personal Branding Intensive",
            description: "Build a powerful personal brand that attracts opportunities. Content strategy, thought leadership, and online presence optimization.",
            duration: "5h 0m",
            difficulty: .intermediate,
            category: .networking,
            type: .subscription,
            tags: ["personal brand", "content", "thought leadership"],
            thumbnailColor: .orange
        )
    ]
    
    // MARK: - All Courses
    var allCourses: [Course] {
        return freeCourses + premiumCourses
    }
    
    // MARK: - Helper Methods
    func getCourse(by id: String) -> Course? {
        return allCourses.first { $0.id == id }
    }
    
    func getCourses(by category: CourseCategory) -> [Course] {
        return allCourses.filter { $0.category == category }
    }
    
    func getCourses(by type: CourseType) -> [Course] {
        return allCourses.filter { $0.type == type }
    }
} 