import SwiftUI
import Contacts
import EventKit

@MainActor
class ProfileViewModel: ObservableObject {
    @Published var userProfile = UserProfile()
    @Published var isLoading = false
    @Published var errorMessage: String?
    
    private let userDefaults = UserDefaults.standard
    private let profileKey = "UserProfile"
    
    init() {
        loadUserProfile()
    }
    
    func loadUserProfile() {
        isLoading = true
        
        // Load from UserDefaults first
        if let data = userDefaults.data(forKey: profileKey),
           let savedProfile = try? JSONDecoder().decode(UserProfile.self, from: data) {
            userProfile = savedProfile
        }
        
        // Try to load additional info from device
        loadDeviceUserInfo()
        
        isLoading = false
    }
    
    func saveUserProfile() {
        userProfile.lastUpdated = Date()
        
        if let data = try? JSONEncoder().encode(userProfile) {
            userDefaults.set(data, forKey: profileKey)
        }
    }
    
    private func loadDeviceUserInfo() {
        // Request contacts access to get user info
        requestContactsAccess { [weak self] granted in
            if granted {
                self?.loadContactInfo()
            }
        }
        
        // Load Apple ID info if available
        loadAppleIDInfo()
    }
    
    private func requestContactsAccess(completion: @escaping (Bool) -> Void) {
        let store = CNContactStore()
        
        switch CNContactStore.authorizationStatus(for: .contacts) {
        case .authorized:
            completion(true)
        case .notDetermined:
            store.requestAccess(for: .contacts) { granted, _ in
                DispatchQueue.main.async {
                    completion(granted)
                }
            }
        default:
            completion(false)
        }
    }
    
    private func loadContactInfo() {
        let store = CNContactStore()
        let keys = [CNContactGivenNameKey, CNContactFamilyNameKey, CNContactEmailAddressesKey] as [CNKeyDescriptor]
        
        do {
            // Try to get "Me" card if available
            if let meCard = try? store.unifiedMeContactMatching(CNContact.predicateForContacts(matchingName: "")) {
                DispatchQueue.main.async {
                    if self.userProfile.firstName?.isEmpty != false {
                        self.userProfile.firstName = meCard.givenName.isEmpty ? nil : meCard.givenName
                    }
                    if self.userProfile.lastName?.isEmpty != false {
                        self.userProfile.lastName = meCard.familyName.isEmpty ? nil : meCard.familyName
                    }
                    if self.userProfile.email?.isEmpty != false && !meCard.emailAddresses.isEmpty {
                        self.userProfile.email = String(meCard.emailAddresses.first?.value ?? "")
                    }
                    self.saveUserProfile()
                }
            }
        } catch {
            print("Error loading contact info: \(error)")
        }
    }
    
    private func loadAppleIDInfo() {
        // Try to get Apple ID from various sources
        // Note: In a real app, you'd use CloudKit or other Apple services
        
        // For now, we'll use placeholder logic
        if userProfile.appleID?.isEmpty != false {
            // Try to infer from email if it's an iCloud email
            if let email = userProfile.email, email.contains("@icloud.com") || email.contains("@me.com") {
                userProfile.appleID = email
            }
        }
        
        saveUserProfile()
    }
    
    func updateMessagingSettings(_ settings: MessagingSettings) {
        userProfile.messagingSettings = settings
        saveUserProfile()
    }
    
    func updateLinkedInSettings(_ settings: LinkedInSettings) {
        userProfile.linkedInSettings = settings
        saveUserProfile()
    }
    
    func updateCalendarSettings(_ settings: CalendarSettings) {
        userProfile.calendarSettings = settings
        saveUserProfile()
    }
    
    func incrementSessionsCompleted() {
        userProfile.totalSessionsCompleted += 1
        updateStreak()
        saveUserProfile()
    }
    
    func addMotivationalMinutes(_ minutes: Int) {
        userProfile.totalMotivationalMinutes += minutes
        saveUserProfile()
    }
    
    private func updateStreak() {
        // Simple streak logic - in a real app, you'd track daily usage
        userProfile.currentStreak += 1
        if userProfile.currentStreak > userProfile.longestStreak {
            userProfile.longestStreak = userProfile.currentStreak
        }
    }
    
    func resetProfile() {
        userProfile = UserProfile()
        userDefaults.removeObject(forKey: profileKey)
    }
    
    // MARK: - Calendar Integration
    func requestCalendarAccess() {
        let eventStore = EKEventStore()
        
        if #available(iOS 17.0, *) {
            eventStore.requestFullAccessToEvents { [weak self] granted, error in
                DispatchQueue.main.async {
                    if granted {
                        self?.userProfile.calendarSettings.isConnected = true
                        self?.saveUserProfile()
                    } else {
                        self?.errorMessage = "Calendar access denied"
                    }
                }
            }
        } else {
            eventStore.requestAccess(to: .event) { [weak self] granted, error in
                DispatchQueue.main.async {
                    if granted {
                        self?.userProfile.calendarSettings.isConnected = true
                        self?.saveUserProfile()
                    } else {
                        self?.errorMessage = "Calendar access denied"
                    }
                }
            }
        }
    }
    
    // MARK: - Demo Data
    func loadDemoData() {
        userProfile.firstName = "John"
        userProfile.lastName = "Seeker"
        userProfile.email = "john.seeker@email.com"
        userProfile.totalSessionsCompleted = 15
        userProfile.totalMotivationalMinutes = 247
        userProfile.currentStreak = 7
        userProfile.longestStreak = 12
        saveUserProfile()
    }
} 