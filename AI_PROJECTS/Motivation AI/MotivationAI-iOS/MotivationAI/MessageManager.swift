import Foundation
import SwiftUI
import UserNotifications
import AVFoundation

@MainActor
class MessageManager: ObservableObject {
    @Published var currentMessage: MotivationalMessage?
    @Published var isDisplayingMessage = false
    @Published var backgroundImages: [String] = []
    @Published var isVoiceoverEnabled = true
    @Published var isShowingAnimatedText = false
    
    private var speechSynthesizer = AVSpeechSynthesizer()
    private var allMessages: [MotivationalMessage] = []
    private let userDefaults = UserDefaults.standard
    
    init() {
        setupBackgroundImages()
        loadAllMessages()
        setupNotifications()
        loadVoiceoverPreference()
    }
    
    private func setupBackgroundImages() {
        backgroundImages = [
            "mountain_sunrise", "forest_river", "ocean_sunset", "desert_dunes",
            "city_skyline", "aurora_lights", "canyon_vista", "lake_reflection",
            "snow_peaks", "tropical_beach", "rolling_hills", "starry_night",
            "misty_forest", "golden_fields", "cliff_ocean", "waterfall_mist",
            "urban_dawn", "autumn_leaves", "spring_blossoms", "winter_frost",
            "volcanic_landscape", "prairie_sunset", "coastal_cliffs", "river_bend",
            "meadow_flowers", "pine_forest", "rocky_shore", "valley_view",
            "sunrise_lake", "moonlit_path"
        ]
    }
    
    private func loadAllMessages() {
        // Include all demo scripts
        allMessages = DemoVideoScripts.allDemoScripts + [
            MotivationalMessage(
                id: "rise_grind_1",
                title: "Rise and Grind!",
                content: "Time to RISE AND GRIND! Your future self is counting on you!",
                author: nil,
                category: .morningWakeUp,
                timeOfDay: .morning,
                tone: .energetic,
                backgroundImageName: "mountain_sunrise",
                audioEnabled: true,
                duration: 15,
                actionPrompt: "Start Your Day Strong"
            )
        ]
    }
    
    private func setupNotifications() {
        UNUserNotificationCenter.current().requestAuthorization(options: [.alert, .sound, .badge]) { granted, error in
            if granted {
                DispatchQueue.main.async {
                    self.scheduleDailyNotifications()
                }
            }
        }
    }
    
    private func scheduleDailyNotifications() {
        let center = UNUserNotificationCenter.current()
        center.removeAllPendingNotificationRequests()
        
        scheduleNotification(hour: 7, title: "Rise and Grind!", body: "Your future self is counting on you.", identifier: "morning_grind")
        scheduleNotification(hour: 12, title: "Midday Momentum", body: "Keep that grind going strong!", identifier: "midday_grind")
        scheduleNotification(hour: 18, title: "Evening Champion", body: "You crushed today! Plan tomorrow's grind.", identifier: "evening_grind")
    }
    
    private func scheduleNotification(hour: Int, title: String, body: String, identifier: String) {
        let content = UNMutableNotificationContent()
        content.title = title
        content.body = body
        content.sound = .default
        
        var dateComponents = DateComponents()
        dateComponents.hour = hour
        dateComponents.minute = 0
        
        let trigger = UNCalendarNotificationTrigger(dateMatching: dateComponents, repeats: true)
        let request = UNNotificationRequest(identifier: identifier, content: content, trigger: trigger)
        
        UNUserNotificationCenter.current().add(request)
    }
    
    // MARK: - Message Display Functions
    func showMessage(_ message: MotivationalMessage) {
        currentMessage = message
        isDisplayingMessage = true
        
        if isVoiceoverEnabled && message.audioEnabled {
            speakMessage(message.content)
        }
    }
    
    func showAnimatedTextMessage(_ message: MotivationalMessage) {
        currentMessage = message
        isShowingAnimatedText = true
        
        if isVoiceoverEnabled && message.audioEnabled {
            // Delay speech to sync with text animation
            DispatchQueue.main.asyncAfter(deadline: .now() + 1.0) {
                self.speakMessage(message.content)
            }
        }
    }
    
    func dismissCurrentMessage() {
        currentMessage = nil
        isDisplayingMessage = false
        isShowingAnimatedText = false
        speechSynthesizer.stopSpeaking(at: .immediate)
    }
    
    private func speakMessage(_ text: String) {
        let utterance = AVSpeechUtterance(string: text)
        utterance.rate = 0.5
        speechSynthesizer.speak(utterance)
    }
    
    func toggleVoiceover() {
        isVoiceoverEnabled.toggle()
        userDefaults.set(isVoiceoverEnabled, forKey: "voiceoverEnabled")
    }
    
    private func loadVoiceoverPreference() {
        isVoiceoverEnabled = userDefaults.bool(forKey: "voiceoverEnabled")
    }
    
    // MARK: - Demo Video Functions
    func getDemoVideosByTimeOfDay(_ timeOfDay: TimeOfDay) -> [MotivationalMessage] {
        return DemoVideoScripts.getScriptsByTimeOfDay(timeOfDay)
    }
    
    func getRandomDemoVideo() -> MotivationalMessage {
        return DemoVideoScripts.getRandomScript()
    }
    
    func getMorningDemos() -> [MotivationalMessage] {
        return DemoVideoScripts.getMorningDemos()
    }
    
    func getMiddayDemos() -> [MotivationalMessage] {
        return DemoVideoScripts.getMiddayDemos()
    }
    
    func getAfternoonDemos() -> [MotivationalMessage] {
        return DemoVideoScripts.getAfternoonDemos()
    }
    
    func getEveningDemos() -> [MotivationalMessage] {
        return DemoVideoScripts.getEveningDemos()
    }
    
    func getToughLoveDemos() -> [MotivationalMessage] {
        return DemoVideoScripts.toughLoveScripts
    }
    
    // MARK: - Original Message Functions
    func getMessageForCurrentTime() -> MotivationalMessage? {
        let hour = Calendar.current.component(.hour, from: Date())
        
        let timeBasedMessages = allMessages.filter { message in
            switch message.timeOfDay {
            case .morning: return hour >= 6 && hour < 11
            case .midday: return hour >= 11 && hour < 14
            case .afternoon: return hour >= 14 && hour < 18
            case .evening: return hour >= 18 && hour < 22
            case .night: return hour >= 22 || hour < 6
            case .anytime: return true
            }
        }
        
        return timeBasedMessages.randomElement() ?? allMessages.randomElement()
    }
    
    func getToughLoveMessage() -> MotivationalMessage? {
        return allMessages.filter { $0.tone == .toughLove }.randomElement()
    }
    
    func getCompassionateMessage() -> MotivationalMessage? {
        return allMessages.filter { $0.tone == .compassionate }.randomElement()
    }
    
    func getActionOrientedMessage() -> MotivationalMessage? {
        return allMessages.filter { $0.tone == .actionFocused }.randomElement()
    }
    
    func celebrateTaskCompletion() {
        let celebrationMessages = allMessages.filter { $0.category == .taskCelebration }
        if let message = celebrationMessages.randomElement() {
            showMessage(message)
        }
    }
} 