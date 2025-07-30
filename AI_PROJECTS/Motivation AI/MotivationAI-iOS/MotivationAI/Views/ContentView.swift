import SwiftUI
import Combine
import AVFoundation

struct ContentView: View {
    @StateObject private var appViewModel = AppViewModel()
    @StateObject private var audioManager = AudioManager()
    
    var body: some View {
        ZStack {
            MainTabView()
                .environmentObject(appViewModel)
            
            // Message overlay
            if let message = appViewModel.currentMessage {
                ZStack {
                    // Background image - use the message's specific background image
                    if !(message.backgroundImageName?.isEmpty ?? true) {
                        // Load background image from Assets.xcassets
                        Image(message.backgroundImageName ?? "")
                            .resizable()
                            .aspectRatio(contentMode: .fill)
                            .ignoresSafeArea(.all)
                            .clipped()
                    } else {
                        // Fallback gradient if no background image specified
                        LinearGradient(
                            gradient: Gradient(colors: [
                                Color.blue.opacity(0.8),
                                Color.purple.opacity(0.6),
                                Color.black.opacity(0.4)
                            ]),
                            startPoint: .topLeading,
                            endPoint: .bottomTrailing
                        )
                        .ignoresSafeArea(.all)
                    }
                    
                    // Dark overlay for text readability
                    Color.black.opacity(0.3)
                        .ignoresSafeArea(.all)
                    
                    VStack(spacing: 20) {
                        // Close button
                        HStack {
                            Spacer()
                            Button(action: {
                                print("🎬 CLOSE BUTTON TAPPED")
                                appViewModel.currentMessage = nil
                            }) {
                                Image(systemName: "xmark.circle.fill")
                                    .font(.title)
                                    .foregroundColor(.white)
                                    .background(Color.black.opacity(0.5))
                                    .clipShape(Circle())
                            }
                            .padding()
                        }
                        
                        Spacer()
                        
                        // Animated message content
                        AnimatedMessageText(
                            text: message.content, 
                            isVisible: true,
                            messageId: message.id,
                            audioManager: audioManager
                        )
                        
                        Spacer()
                        
                        // Action button
                        Button(action: {
                            print("🎬 LET'S GO BUTTON TAPPED")
                            appViewModel.currentMessage = nil
                        }) {
                            Text(message.actionPrompt ?? "LET'S GO!")
                                .font(.title2)
                                .fontWeight(.bold)
                                .foregroundColor(.black)
                                .padding(.horizontal, 40)
                                .padding(.vertical, 15)
                                .background(Color.white)
                                .cornerRadius(25)
                        }
                        .padding(.bottom, 50)
                    }
                }
                .transition(AnyTransition.opacity)
                .animation(.easeInOut(duration: 0.3), value: appViewModel.currentMessage != nil)
            }
        }
        .onReceive(appViewModel.$currentMessage) { message in
            if let message = message {
                print("✅ Message received in ContentView: \(message.title)")
                // Start audio playback if available
                if audioManager.hasAudioForMessage(message.id) {
                    print("🎵 Starting audio for message: \(message.id)")
                    audioManager.playAudioForMessage(message.id)
                }
            } else {
                print("✅ Message cleared in ContentView")
                // Stop audio when message is dismissed
                audioManager.stopAudio()
            }
        }
    }
}

// Function to split text into phrases and clauses
func splitIntoPhrasesAndClauses(_ text: String) -> [String] {
    // Split by common punctuation that indicates phrase/clause boundaries
    let delimiters = [",", ".", "!", "?", ";", ":", " and ", " or ", " but ", " so "]
    var phrases: [String] = []
    var currentPhrase = text
    
    // First split by punctuation
    for delimiter in delimiters {
        let components = currentPhrase.components(separatedBy: delimiter)
        if components.count > 1 {
            phrases = []
            for i in 0..<components.count {
                var phrase = components[i].trimmingCharacters(in: .whitespaces)
                if i < components.count - 1 && delimiter != " and " && delimiter != " or " && delimiter != " but " && delimiter != " so " {
                    phrase += delimiter
                }
                if !phrase.isEmpty {
                    phrases.append(phrase)
                }
            }
            break
        }
    }
    
    // If no punctuation found, group words into 2-3 word phrases
    if phrases.isEmpty {
        let words = text.components(separatedBy: " ").filter { !$0.isEmpty }
        var i = 0
        while i < words.count {
            let phraseLength = min(3, words.count - i) // 2-3 words per phrase
            let phrase = Array(words[i..<i+phraseLength]).joined(separator: " ")
            phrases.append(phrase)
            i += phraseLength
        }
    }
    
    return phrases
}

// MARK: - Animated Message Text Component
struct AnimatedMessageText: View {
    let text: String
    let isVisible: Bool
    let messageId: String
    @ObservedObject var audioManager: AudioManager
    
    @State private var textChunks: [String] = []
    @State private var currentChunkIndex = 0
    
    var body: some View {
        VStack(alignment: .center, spacing: 16) {
            // Audio-synchronized display
            if audioManager.hasAudioForMessage(messageId) && audioManager.isPlaying {
                if let currentTimestamp = audioManager.currentTimestamp {
                    // Display current audio phrase with TikTok-style bubbles
                    FlowLayout(alignment: .center, spacing: 8) {
                        let phrases = splitIntoPhrasesAndClauses(currentTimestamp.text)
                        ForEach(Array(phrases.enumerated()), id: \.offset) { phraseIndex, phrase in
                            if !phrase.isEmpty {
                                Text(phrase)
                                    .font(.title2)  // TikTok-style sizing
                                    .fontWeight(.semibold)  // TikTok-style weight
                                    .foregroundColor(.white)
                                    .padding(.horizontal, 12)  // 12 pts left and right padding
                                    .padding(.vertical, 6)
                                    .background(
                                        RoundedRectangle(cornerRadius: 0)  // 0 pt corner radius (rectangular)
                                            .fill(Color.black.opacity(0.9))  // TikTok-style background
                                            .shadow(color: .black.opacity(0.3), radius: 1, x: 0, y: 1)
                                    )
                                    .scaleEffect(1.1)  // Slightly larger for emphasis
                                    .animation(.easeInOut(duration: 0.2), value: currentTimestamp.text)
                            }
                        }
                    }
                    .transition(.scale.combined(with: .opacity))
                }
            }
            // Fallback to original timer-based system when no audio
            else if currentChunkIndex < textChunks.count {
                let currentChunk = textChunks[currentChunkIndex]
                
                // Split current chunk into lines for display
                let lines = currentChunk.components(separatedBy: "\n").filter { !$0.isEmpty }
                
                ForEach(Array(lines.enumerated()), id: \.offset) { index, line in
                    // Create a flowing layout of phrases with individual backgrounds
                    FlowLayout(alignment: .center, spacing: 8) {
                        let phrases = splitIntoPhrasesAndClauses(line)
                        ForEach(Array(phrases.enumerated()), id: \.offset) { phraseIndex, phrase in
                            if !phrase.isEmpty {
                                Text(phrase)
                                    .font(.title2)  // TikTok-style sizing
                                    .fontWeight(.semibold)  // TikTok-style weight
                                    .foregroundColor(.white)
                                    .padding(.horizontal, 12)  // 12 pts left and right padding
                                    .padding(.vertical, 6)
                                    .background(
                                        RoundedRectangle(cornerRadius: 0)  // 0 pt corner radius (rectangular)
                                            .fill(Color.black.opacity(0.9))  // TikTok-style background
                                            .shadow(color: .black.opacity(0.3), radius: 1, x: 0, y: 1)
                                    )
                            }
                        }
                    }
                    .opacity(1.0)
                    .scaleEffect(1.0)
                    .animation(.easeInOut(duration: 0.3), value: currentChunkIndex)
                }
            }
        }
        .onAppear {
            if isVisible {
                setupTextChunks()
                startAnimation()
            }
        }
        .onChange(of: isVisible) { newValue in
            if newValue {
                setupTextChunks()
                startAnimation()
            } else {
                currentChunkIndex = 0
            }
        }
    }
    
    private func setupTextChunks() {
        // Split text into impactful chunks of 2-3 sentences each
        let sentences = text.components(separatedBy: CharacterSet(charactersIn: ".!?"))
            .map { $0.trimmingCharacters(in: .whitespacesAndNewlines) }
            .filter { !$0.isEmpty }
        
        var chunks: [String] = []
        var currentChunk = ""
        var sentenceCount = 0
        
        for sentence in sentences {
            if sentenceCount == 0 {
                currentChunk = sentence.capitalized
            } else {
                currentChunk += "\n" + sentence.capitalized
            }
            
            sentenceCount += 1
            
            // Create chunk after 2-3 sentences or when we hit certain keywords
            let shouldBreak = sentenceCount >= 2 || 
                            sentence.uppercased().contains("WHAT") ||
                            sentence.uppercased().contains("SO") ||
                            sentence.uppercased().contains("NOW") ||
                            sentence.uppercased().contains("YES") ||
                            sentence.uppercased().contains("NO")
            
            if shouldBreak {
                if !currentChunk.isEmpty {
                    chunks.append(currentChunk)
                }
                currentChunk = ""
                sentenceCount = 0
            }
        }
        
        // Add any remaining content
        if !currentChunk.isEmpty {
            chunks.append(currentChunk)
        }
        
        textChunks = chunks
    }
    
    private func startAnimation() {
        currentChunkIndex = 0
        
        // Show each chunk for 3 seconds, then clear and show next
        Timer.scheduledTimer(withTimeInterval: 3.0, repeats: true) { timer in
            if currentChunkIndex < textChunks.count - 1 {
                currentChunkIndex += 1
            } else {
                timer.invalidate()
            }
        }
    }
}

// Custom FlowLayout for wrapping text with individual backgrounds
struct FlowLayout: Layout {
    var alignment: Alignment = .center
    var spacing: CGFloat = 10
    
    func sizeThatFits(proposal: ProposedViewSize, subviews: Subviews, cache: inout ()) -> CGSize {
        let result = FlowResult(
            in: proposal.replacingUnspecifiedDimensions(),
            subviews: subviews,
            alignment: alignment,
            spacing: spacing
        )
        return result.bounds
    }
    
    func placeSubviews(in bounds: CGRect, proposal: ProposedViewSize, subviews: Subviews, cache: inout ()) {
        let result = FlowResult(
            in: proposal.replacingUnspecifiedDimensions(),
            subviews: subviews,
            alignment: alignment,
            spacing: spacing
        )
        for (index, subview) in subviews.enumerated() {
            subview.place(at: result.positions[index], proposal: .unspecified)
        }
    }
}

struct FlowResult {
    var bounds = CGSize.zero
    var positions: [CGPoint] = []
    
    init(in maxSize: CGSize, subviews: LayoutSubviews, alignment: Alignment, spacing: CGFloat) {
        var currentRow = 0
        var currentX: CGFloat = 0
        var currentY: CGFloat = 0
        var rowHeight: CGFloat = 0
        var rowWidths: [CGFloat] = []
        
        for subview in subviews {
            let subviewSize = subview.sizeThatFits(.unspecified)
            
            if currentX + subviewSize.width > maxSize.width && currentX > 0 {
                // Move to next row
                rowWidths.append(currentX - spacing)
                currentRow += 1
                currentY += rowHeight + spacing
                currentX = 0
                rowHeight = 0
            }
            
            positions.append(CGPoint(x: currentX, y: currentY))
            currentX += subviewSize.width + spacing
            rowHeight = max(rowHeight, subviewSize.height)
            bounds.width = max(bounds.width, currentX - spacing)
        }
        
        if currentX > 0 {
            rowWidths.append(currentX - spacing)
        }
        
        bounds.height = currentY + rowHeight
        
        // Center align the rows
        if alignment.horizontal == .center {
            var rowIndex = 0
            var positionIndex = 0
            
            for (index, position) in positions.enumerated() {
                if index > 0 && positions[index].y > positions[index - 1].y {
                    rowIndex += 1
                    positionIndex = 0
                }
                
                if rowIndex < rowWidths.count {
                    let rowWidth = rowWidths[rowIndex]
                    let offset = (bounds.width - rowWidth) / 2
                    positions[index].x += offset
                }
                positionIndex += 1
            }
        }
    }
}

struct MainTabView: View {
    var body: some View {
        TabView {
            DashboardView()
                .tabItem {
                    Label("Home", systemImage: "house.fill")
                }
                .tag(0)
            
            DemoVideosView()
                .tabItem {
                    Label("Let's Go!", systemImage: "bolt.fill")
                }
                .tag(1)
            
            AIGeneratorEmbeddedView()
                .tabItem {
                    Label("AI Create", systemImage: "brain.head.profile")
                }
                .tag(2)
            
            TasksView()
                .tabItem {
                    Label("Tasks", systemImage: "list.bullet")
                }
                .tag(3)
            
            LearnView()
                .tabItem {
                    Label("Learn", systemImage: "book.fill")
                }
                .tag(4)
            
            ProfileView()
                .tabItem {
                    Label("Profile", systemImage: "person.fill")
                }
                .tag(5)
        }
        .preferredColorScheme(.dark)
    }
}

// MARK: - Learn View Implementation
struct LearnView: View {
    @State private var selectedFilter: CourseFilter = .all
    @State private var courseProvider = CourseDataProvider.shared
    @State private var showPremiumSheet = false
    @State private var selectedCourse: Course?
    
    var body: some View {
        NavigationView {
            ZStack {
                // Pure black background - no grays
                Color(red: 0, green: 0, blue: 0)
                    .ignoresSafeArea()
                
                ScrollView(.vertical, showsIndicators: true) {
                    VStack(spacing: 16) { // Reduced spacing
                        // Header section
                        headerSection
                        
                        // Filter tabs
                        filterSection
                        
                        // Course list
                        courseListSection
                        
                        // Extra bottom padding for better scrolling
                        Spacer()
                            .frame(height: 100)
                    }
                }
                .scrollIndicators(.visible)
            }
            .navigationTitle("")
            .navigationBarTitleDisplayMode(.inline)
        }
        .sheet(item: $selectedCourse) { course in
            CourseDetailSheet(course: course)
        }
        .sheet(isPresented: $showPremiumSheet) {
            PremiumUpgradeSheet()
        }
    }
    
    // MARK: - Header Section
    private var headerSection: some View {
        VStack(spacing: 8) { // Reduced spacing
            HStack {
                VStack(alignment: .leading, spacing: 2) { // Reduced spacing
                    Text("Learn & Grow")
                        .font(.system(size: 26, weight: .bold)) // Reduced from 28
                        .foregroundColor(.white)
                    
                    Text("Career development courses")
                        .font(.system(size: 14, weight: .medium)) // Reduced from 16
                        .foregroundColor(.white.opacity(0.7))
                }
                
                Spacer()
                
                // Progress indicator
                VStack(spacing: 2) {
                    Text("\(completedCourses)")
                        .font(.system(size: 20, weight: .bold)) // Reduced from 24
                        .foregroundColor(.green)
                    
                    Text("Completed")
                        .font(.system(size: 12, weight: .medium)) // Reduced from 14
                        .foregroundColor(.white.opacity(0.6))
                }
            }
            .padding(.horizontal, 16) // Reduced from 20
            .padding(.top, 8) // Reduced from 20
        }
    }
    
    // MARK: - Filter Section
    private var filterSection: some View {
        HStack(spacing: 0) {
            ForEach(CourseFilter.allCases, id: \.self) { filter in
                Button(action: {
                    selectedFilter = filter
                }) {
                    VStack(spacing: 4) { // Reduced spacing
                        Text(filter.rawValue)
                            .font(.system(size: 13, weight: .semibold)) // Reduced from 14
                            .foregroundColor(selectedFilter == filter ? .black : .white.opacity(0.7))
                        
                        Text("\(courseCount(for: filter))")
                            .font(.system(size: 16, weight: .bold)) // Reduced from 18
                            .foregroundColor(selectedFilter == filter ? .black : .orange)
                    }
                    .frame(maxWidth: .infinity)
                    .frame(height: 50) // Reduced from 60
                    .background(
                        RoundedRectangle(cornerRadius: 8) // Reduced from 12
                            .fill(selectedFilter == filter ? .orange : Color.clear)
                    )
                }
                .buttonStyle(PlainButtonStyle())
            }
        }
        .padding(.horizontal, 16) // Reduced from 20
    }
    
    // MARK: - Course List Section
    private var courseListSection: some View {
        VStack(spacing: 8) { // Reduced spacing
            HStack {
                Text("\(selectedFilter.rawValue) Courses")
                    .font(.system(size: 16, weight: .semibold)) // Reduced from 18
                    .foregroundColor(.white)
                
                Spacer()
                
                if selectedFilter == .premium {
                    Button("Upgrade") {
                        showPremiumSheet = true
                    }
                    .font(.system(size: 12, weight: .semibold)) // Reduced from 14
                    .foregroundColor(.orange)
                }
            }
            .padding(.horizontal, 16) // Reduced from 20
            
            LazyVStack(spacing: 12, pinnedViews: []) { // Better scrolling performance
                ForEach(filteredCourses) { course in
                    CourseCard(
                        course: course,
                        onTap: {
                            if course.type == .free {
                                selectedCourse = course
                            } else {
                                showPremiumSheet = true
                            }
                        }
                    )
                    .animation(.easeInOut(duration: 0.2), value: selectedFilter)
                }
            }
            .padding(.horizontal, 16) // Reduced from 20
        }
    }
    
    // MARK: - Helper Properties
    private var filteredCourses: [Course] {
        switch selectedFilter {
        case .all: return courseProvider.allCourses
        case .free: return courseProvider.freeCourses
        case .premium: return courseProvider.premiumCourses
        }
    }
    
    private var completedCourses: Int {
        return courseProvider.allCourses.filter { course in
            let key = "completed_lessons_\(course.id)"
            if let data = UserDefaults.standard.data(forKey: key),
               let completedLessons = try? JSONDecoder().decode(Set<String>.self, from: data) {
                return !course.lessons.isEmpty && completedLessons.count == course.lessons.count
            }
            return false
        }.count
    }
    
    private func courseCount(for filter: CourseFilter) -> Int {
        switch filter {
        case .all: return courseProvider.allCourses.count
        case .free: return courseProvider.freeCourses.count
        case .premium: return courseProvider.premiumCourses.count
        }
    }
}

// MARK: - Course Filter Enum
enum CourseFilter: String, CaseIterable {
    case all = "All"
    case free = "Free"
    case premium = "Premium"
}

// MARK: - Course Card
struct CourseCard: View {
    let course: Course
    let onTap: () -> Void
    @State private var completedLessons: Set<String> = []
    
    var body: some View {
        Button(action: onTap) {
            HStack(spacing: 12) { // Reduced spacing
                // Course thumbnail with color
                RoundedRectangle(cornerRadius: 8) // Reduced from 12
                    .fill(course.thumbnailColor.swiftUIColor)
                    .frame(width: 60, height: 60) // Reduced from 70
                    .overlay(
                        ZStack {
                            Image(systemName: course.category.icon)
                                .font(.system(size: 24, weight: .medium)) // Reduced from 28
                                .foregroundColor(.white)
                            
                            // Progress indicator for courses with lessons
                            if !course.lessons.isEmpty && completionPercentage > 0 {
                                VStack {
                                    Spacer()
                                    HStack {
                                        Spacer()
                                        Text("\(Int(completionPercentage))%")
                                            .font(.system(size: 8, weight: .bold))
                                            .foregroundColor(.white)
                                            .padding(2)
                                            .background(.black.opacity(0.7))
                                            .cornerRadius(4)
                                    }
                                }
                                .padding(4)
                            }
                        }
                    )
                
                // Course content
                VStack(alignment: .leading, spacing: 2) { // Reduced spacing
                    HStack {
                        Text(course.title)
                            .font(.system(size: 14, weight: .semibold)) // Reduced from 16
                            .foregroundColor(.white)
                            .lineLimit(2)
                        
                        Spacer()
                        
                        // Course type badge
                        courseTypeBadge
                    }
                    
                    Text(course.description)
                        .font(.system(size: 12, weight: .regular)) // Reduced from 14
                        .foregroundColor(.white.opacity(0.7))
                        .lineLimit(2)
                    
                    // Progress bar for courses with lessons
                    if !course.lessons.isEmpty {
                        HStack(spacing: 4) {
                            ProgressView(value: completionPercentage, total: 100)
                                .progressViewStyle(LinearProgressViewStyle(tint: course.thumbnailColor.swiftUIColor))
                                .background(.white.opacity(0.2))
                                .cornerRadius(2)
                                .frame(height: 4)
                            
                            Text("\(completedLessons.count)/\(course.lessons.count)")
                                .font(.system(size: 8, weight: .medium))
                                .foregroundColor(.white.opacity(0.6))
                        }
                    }
                    
                    HStack(spacing: 8) { // Reduced spacing
                        // Duration
                        HStack(spacing: 2) {
                            Image(systemName: "clock")
                                .font(.system(size: 10)) // Reduced from 12
                                .foregroundColor(.white.opacity(0.6))
                            
                            Text(course.duration)
                                .font(.system(size: 10, weight: .medium)) // Reduced from 12
                                .foregroundColor(.white.opacity(0.6))
                        }
                        
                        // Difficulty
                        Text(course.difficulty.rawValue)
                            .font(.system(size: 10, weight: .medium)) // Reduced from 12
                            .foregroundColor(course.difficulty.color.swiftUIColor)
                            .padding(.horizontal, 6) // Reduced from 8
                            .padding(.vertical, 2) // Reduced from 4
                            .background(
                                RoundedRectangle(cornerRadius: 4) // Reduced from 6
                                    .fill(course.difficulty.color.swiftUIColor.opacity(0.2))
                            )
                        
                        Spacer()
                        
                        // Completion status
                        if completionPercentage >= 100 {
                            Image(systemName: "checkmark.circle.fill")
                                .font(.system(size: 12))
                                .foregroundColor(.green)
                        }
                        
                        // Price for premium courses
                        if let price = course.price {
                            Text("$\(Int(price))")
                                .font(.system(size: 12, weight: .bold)) // Reduced from 14
                                .foregroundColor(.orange)
                        }
                    }
                }
                
                // Chevron
                Image(systemName: "chevron.right")
                    .font(.system(size: 12, weight: .medium)) // Reduced from 14
                    .foregroundColor(.white.opacity(0.4))
            }
            .padding(.vertical, 12) // Reduced from 16
        }
        .buttonStyle(PlainButtonStyle())
        .onAppear {
            loadCompletedLessons()
        }
    }
    
    private var courseTypeBadge: some View {
        Text(course.type.displayText)
            .font(.system(size: 10, weight: .bold)) // Reduced from 12
            .foregroundColor(course.type == .free ? .black : .white)
            .padding(.horizontal, 8) // Reduced from 10
            .padding(.vertical, 2) // Reduced from 4
            .background(
                RoundedRectangle(cornerRadius: 6) // Reduced from 8
                    .fill(course.type.color.swiftUIColor)
            )
    }
    
    // MARK: - Helper Properties
    private var completionPercentage: Double {
        guard !course.lessons.isEmpty else { return 0 }
        let completed = Double(completedLessons.count)
        let total = Double(course.lessons.count)
        return (completed / total) * 100
    }
    
    // MARK: - Helper Methods
    private func loadCompletedLessons() {
        let key = "completed_lessons_\(course.id)"
        if let data = UserDefaults.standard.data(forKey: key),
           let lessons = try? JSONDecoder().decode(Set<String>.self, from: data) {
            completedLessons = lessons
        }
    }
}

// MARK: - Premium Upgrade Sheet
struct PremiumUpgradeSheet: View {
    @Environment(\.dismiss) private var dismiss
    
    var body: some View {
        NavigationView {
            ZStack {
                Color(red: 0, green: 0, blue: 0).ignoresSafeArea() // Pure black
                
                VStack(spacing: 24) {
                    Image(systemName: "crown.fill")
                        .font(.system(size: 50))
                        .foregroundColor(.orange)
                    
                    VStack(spacing: 16) {
                        Text("Unlock Premium Courses")
                            .font(.title)
                            .fontWeight(.bold)
                            .foregroundColor(.white)
                        
                        Text("Access advanced courses, exclusive content, and personalized career coaching.")
                            .font(.body)
                            .foregroundColor(.white.opacity(0.8))
                            .multilineTextAlignment(.center)
                    }
                    
                    VStack(spacing: 12) {
                        Button("Subscribe - $9.99/month") {
                            // Handle subscription
                            dismiss()
                        }
                        .font(.headline)
                        .foregroundColor(.white)
                        .frame(maxWidth: .infinity)
                        .frame(height: 50)
                        .background(.orange)
                        .cornerRadius(12)
                        
                        Button("View Individual Courses") {
                            // Handle individual purchase
                            dismiss()
                        }
                        .font(.subheadline)
                        .foregroundColor(.orange)
                    }
                    
                    Spacer()
                }
                .padding(24)
            }
            .preferredColorScheme(.dark)
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button("Close") {
                        dismiss()
                    }
                    .foregroundColor(.white)
                }
            }
        }
    }
}

// MARK: - Course Detail Sheet
struct CourseDetailSheet: View {
    let course: Course
    @Environment(\.dismiss) private var dismiss
    @EnvironmentObject private var profileManager: ProfileManager
    @State private var courseProvider = CourseDataProvider.shared
    @State private var completedLessons: Set<String> = []
    @State private var selectedLesson: Lesson? = nil
    @State private var showLessonDetail = false
    
    var body: some View {
        NavigationView {
            ZStack {
                Color(red: 0, green: 0, blue: 0).ignoresSafeArea() // Pure black
                
                if let selectedLesson = selectedLesson, showLessonDetail {
                    // Lesson Detail View
                    lessonDetailView(lesson: selectedLesson)
                } else {
                    // Course Overview
                    courseOverviewView
                }
            }
        }
        .onAppear {
            loadCompletedLessons()
        }
    }
    
    private var courseOverviewView: some View {
        ScrollView(.vertical, showsIndicators: true) {
            VStack(alignment: .leading, spacing: 20) {
                // Course header
                VStack(alignment: .leading, spacing: 12) {
                    Text(course.title)
                        .font(.title)
                        .fontWeight(.bold)
                        .foregroundColor(.white)
                    
                    Text(course.description)
                        .font(.body)
                        .foregroundColor(.white.opacity(0.8))
                        .lineLimit(nil)
                        .multilineTextAlignment(.leading)
                        .fixedSize(horizontal: false, vertical: true)
                    
                    HStack {
                        Text(course.duration)
                            .font(.subheadline)
                            .foregroundColor(.white.opacity(0.6))
                        
                        Spacer()
                        
                        Text(course.difficulty.rawValue.capitalized)
                            .font(.subheadline)
                            .fontWeight(.medium)
                            .foregroundColor(course.thumbnailColor.swiftUIColor)
                    }
                    
                    // Progress bar
                    ProgressView(value: progressPercentage)
                        .progressViewStyle(LinearProgressViewStyle(tint: course.thumbnailColor.swiftUIColor))
                        .background(Color.white.opacity(0.2))
                    
                    Text("\(Int(progressPercentage * 100))% Complete")
                        .font(.caption)
                        .foregroundColor(.white.opacity(0.6))
                }
                .padding(.horizontal, 20)
                .padding(.top, 20)
                
                // Lessons list
                VStack(alignment: .leading, spacing: 16) {
                    Text("Course Content - Tap to Complete")
                        .font(.headline)
                        .fontWeight(.semibold)
                        .foregroundColor(.white)
                        .padding(.horizontal, 20)
                    
                    ForEach(course.lessons.sorted(by: { $0.order < $1.order })) { lesson in
                        lessonRow(lesson: lesson)
                    }
                }
                
                // Extra bottom padding for better scrolling experience
                Spacer()
                    .frame(height: 100)
            }
        }
        .scrollIndicators(.visible)
        .navigationTitle("")
        .navigationBarTitleDisplayMode(.inline)
        .toolbar {
            ToolbarItem(placement: .navigationBarTrailing) {
                Button("Close") {
                    dismiss()
                }
                .foregroundColor(.white)
            }
        }
    }
    
    private func lessonRow(lesson: Lesson) -> some View {
        Button(action: {
            selectedLesson = lesson
            showLessonDetail = true
        }) {
            HStack(spacing: 12) {
                // Completion indicator
                ZStack {
                    Circle()
                        .stroke(completedLessons.contains(lesson.id) ? .clear : .white.opacity(0.3), lineWidth: 2)
                        .frame(width: 24, height: 24)
                    
                    if completedLessons.contains(lesson.id) {
                        Circle()
                            .fill(course.thumbnailColor.swiftUIColor)
                            .frame(width: 24, height: 24)
                        Image(systemName: "checkmark")
                            .font(.system(size: 12, weight: .bold))
                            .foregroundColor(.white)
                    } else {
                        Text("\(lesson.order)")
                            .font(.system(size: 12, weight: .medium))
                            .foregroundColor(.white.opacity(0.8))
                    }
                }
                
                // Lesson info
                VStack(alignment: .leading, spacing: 4) {
                    Text(lesson.title)
                        .font(.system(size: 16, weight: .medium))
                        .foregroundColor(.white)
                        .strikethrough(completedLessons.contains(lesson.id))
                    
                    HStack {
                        Text(lesson.duration)
                            .font(.system(size: 14))
                            .foregroundColor(.white.opacity(0.6))
                        
                        if completedLessons.contains(lesson.id) {
                            Text("• Completed")
                                .font(.system(size: 14))
                                .foregroundColor(course.thumbnailColor.swiftUIColor)
                        }
                    }
                }
                
                Spacer()
                
                Image(systemName: "chevron.right")
                    .font(.system(size: 14))
                    .foregroundColor(.white.opacity(0.4))
            }
            .padding(.horizontal, 20)
            .padding(.vertical, 12)
        }
        .buttonStyle(PlainButtonStyle())
    }
    
    private func lessonDetailView(lesson: Lesson) -> some View {
        ScrollView(.vertical, showsIndicators: true) {
            VStack(alignment: .leading, spacing: 20) {
                // Back button and lesson header
                VStack(alignment: .leading, spacing: 16) {
                    Button(action: {
                        showLessonDetail = false
                        selectedLesson = nil
                    }) {
                        HStack(spacing: 8) {
                            Image(systemName: "chevron.left")
                                .font(.system(size: 16, weight: .medium))
                            Text("Back to Course")
                                .font(.system(size: 16, weight: .medium))
                        }
                        .foregroundColor(course.thumbnailColor.swiftUIColor)
                    }
                    .padding(.horizontal, 20)
                    .padding(.top, 20)
                    
                    VStack(alignment: .leading, spacing: 8) {
                        Text("Lesson \(lesson.order)")
                            .font(.subheadline)
                            .foregroundColor(course.thumbnailColor.swiftUIColor)
                        
                        Text(lesson.title)
                            .font(.title2)
                            .fontWeight(.bold)
                            .foregroundColor(.white)
                        
                        Text(lesson.duration)
                            .font(.subheadline)
                            .foregroundColor(.white.opacity(0.6))
                    }
                    .padding(.horizontal, 20)
                }
                
                // Lesson content with proper markdown rendering
                VStack(alignment: .leading, spacing: 16) {
                    MarkdownText(content: lesson.content)
                }
                .padding(.horizontal, 20)
                
                // Complete button section
                VStack(spacing: 16) {
                    if !completedLessons.contains(lesson.id) {
                        Button(action: {
                            markLessonComplete(lesson)
                            // Wait 1 second then return to course automatically
                            DispatchQueue.main.asyncAfter(deadline: .now() + 1.0) {
                                showLessonDetail = false
                                selectedLesson = nil
                            }
                        }) {
                            HStack {
                                Image(systemName: "checkmark.circle.fill")
                                    .font(.system(size: 18))
                                Text("Mark Complete")
                                    .font(.system(size: 16, weight: .semibold))
                            }
                            .foregroundColor(.white)
                            .frame(maxWidth: .infinity)
                            .padding()
                            .background(course.thumbnailColor.swiftUIColor)
                            .cornerRadius(12)
                        }
                        .padding(.horizontal, 20)
                    } else {
                        HStack {
                            Image(systemName: "checkmark.circle.fill")
                                .font(.system(size: 18))
                            Text("Lesson Completed")
                                .font(.system(size: 16, weight: .semibold))
                        }
                        .foregroundColor(course.thumbnailColor.swiftUIColor)
                        .frame(maxWidth: .infinity)
                        .padding()
                        .background(course.thumbnailColor.swiftUIColor.opacity(0.2))
                        .cornerRadius(12)
                        .padding(.horizontal, 20)
                    }
                    
                    Button(action: {
                        showLessonDetail = false
                        selectedLesson = nil
                    }) {
                        Text("Back to Course")
                            .font(.system(size: 16, weight: .medium))
                            .foregroundColor(.white.opacity(0.8))
                            .frame(maxWidth: .infinity)
                            .padding()
                            .background(Color.white.opacity(0.1))
                            .cornerRadius(12)
                    }
                    .padding(.horizontal, 20)
                }
                .padding(.top, 20)
                
                // Extra bottom padding to ensure buttons are accessible
                Spacer()
                    .frame(height: 120)
            }
        }
        .scrollIndicators(.visible)
        .navigationTitle("")
        .navigationBarTitleDisplayMode(.inline)
        .toolbar {
            ToolbarItem(placement: .navigationBarTrailing) {
                Button("Close") {
                    dismiss()
                }
                .foregroundColor(.white)
            }
        }
    }
    
    private var progressPercentage: Double {
        guard !course.lessons.isEmpty else { return 0.0 }
        let completedCount = course.lessons.filter { completedLessons.contains($0.id) }.count
        return Double(completedCount) / Double(course.lessons.count)
    }
    
    private func loadCompletedLessons() {
        let key = "completed_lessons_\(course.id)"
        if let data = UserDefaults.standard.data(forKey: key),
           let lessons = try? JSONDecoder().decode(Set<String>.self, from: data) {
            completedLessons = lessons
        }
    }
    
    private func markLessonComplete(_ lesson: Lesson) {
        completedLessons.insert(lesson.id)
        saveCompletedLessons()
        
        // Notify ProfileManager to update the dashboard
        profileManager.notifyLessonCompleted()
    }
    
    private func saveCompletedLessons() {
        let key = "completed_lessons_\(course.id)"
        if let data = try? JSONEncoder().encode(completedLessons) {
            UserDefaults.standard.set(data, forKey: key)
        }
    }
}

// MARK: - Markdown Text Renderer
struct MarkdownText: View {
    let content: String
    
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            ForEach(parseMarkdown(content), id: \.id) { element in
                switch element.type {
                case .heading1:
                    Text(element.text)
                        .font(.title)
                        .fontWeight(.bold)
                        .foregroundColor(.white)
                        .padding(.top, 20)
                        .padding(.bottom, 8)
                        
                case .heading2:
                    Text(element.text)
                        .font(.title2)
                        .fontWeight(.semibold)
                        .foregroundColor(.white)
                        .padding(.top, 16)
                        .padding(.bottom, 6)
                        
                case .heading3:
                    Text(element.text)
                        .font(.headline)
                        .fontWeight(.medium)
                        .foregroundColor(.white)
                        .padding(.top, 12)
                        .padding(.bottom, 4)
                        
                case .bold:
                    Text(element.text)
                        .font(.body)
                        .fontWeight(.bold)
                        .foregroundColor(.white)
                        .padding(.vertical, 2)
                        
                case .bulletList:
                    VStack(alignment: .leading, spacing: 4) {
                        ForEach(element.listItems, id: \.self) { item in
                            HStack(alignment: .top, spacing: 8) {
                                Text("•")
                                    .foregroundColor(.orange)
                                    .fontWeight(.bold)
                                Text(item)
                                    .font(.body)
                                    .foregroundColor(.white)
                                Spacer()
                            }
                        }
                    }
                    .padding(.vertical, 4)
                    
                case .checkboxList:
                    VStack(alignment: .leading, spacing: 6) {
                        ForEach(element.checkboxItems, id: \.id) { item in
                            HStack(alignment: .top, spacing: 10) {
                                Image(systemName: item.isChecked ? "checkmark.square.fill" : "square")
                                    .foregroundColor(item.isChecked ? .green : .white.opacity(0.7))
                                    .font(.system(size: 16))
                                Text(item.text)
                                    .font(.body)
                                    .foregroundColor(.white)
                                    .strikethrough(item.isChecked)
                                Spacer()
                            }
                        }
                    }
                    .padding(.vertical, 4)
                    
                case .codeBlock:
                    Text(element.text)
                        .font(.system(.body, design: .monospaced))
                        .foregroundColor(.green)
                        .padding()
                        .background(Color.white.opacity(0.1))
                        .cornerRadius(8)
                        .padding(.vertical, 4)
                        
                case .table:
                    ScrollView(.horizontal, showsIndicators: false) {
                        VStack(alignment: .leading, spacing: 2) {
                            ForEach(element.tableRows, id: \.self) { row in
                                HStack(spacing: 1) {
                                    ForEach(row, id: \.self) { cell in
                                        Text(cell)
                                            .font(.caption)
                                            .foregroundColor(.white)
                                            .padding(8)
                                            .frame(minWidth: 80, alignment: .leading)
                                            .background(Color.white.opacity(0.1))
                                    }
                                }
                            }
                        }
                    }
                    .padding(.vertical, 4)
                    
                case .paragraph:
                    Text(parseInlineMarkdown(element.text))
                        .font(.body)
                        .foregroundColor(.white)
                        .lineLimit(nil)
                        .multilineTextAlignment(.leading)
                        .fixedSize(horizontal: false, vertical: true)
                        .padding(.vertical, 2)
                        
                case .separator:
                    Rectangle()
                        .fill(Color.white.opacity(0.3))
                        .frame(height: 1)
                        .padding(.vertical, 12)
                }
            }
        }
    }
    
    private func parseMarkdown(_ content: String) -> [MarkdownElement] {
        let lines = content.components(separatedBy: .newlines)
        var elements: [MarkdownElement] = []
        var currentParagraph = ""
        var inCodeBlock = false
        var codeBlockContent = ""
        var inTable = false
        var tableRows: [[String]] = []
        var inBulletList = false
        var bulletItems: [String] = []
        var inCheckboxList = false
        var checkboxItems: [CheckboxItem] = []
        
        for line in lines {
            let trimmedLine = line.trimmingCharacters(in: .whitespaces)
            
            // Handle code blocks
            if trimmedLine.hasPrefix("```") {
                if inCodeBlock {
                    elements.append(MarkdownElement(type: .codeBlock, text: codeBlockContent.trimmingCharacters(in: .whitespacesAndNewlines)))
                    codeBlockContent = ""
                    inCodeBlock = false
                } else {
                    finalizeParagraph(&currentParagraph, &elements)
                    inCodeBlock = true
                }
                continue
            }
            
            if inCodeBlock {
                codeBlockContent += line + "\n"
                continue
            }
            
            // Handle separators
            if trimmedLine == "---" {
                finalizeParagraph(&currentParagraph, &elements)
                finalizeBulletList(&bulletItems, &inBulletList, &elements)
                finalizeCheckboxList(&checkboxItems, &inCheckboxList, &elements)
                elements.append(MarkdownElement(type: .separator, text: ""))
                continue
            }
            
            // Handle headings
            if trimmedLine.hasPrefix("# ") {
                finalizeParagraph(&currentParagraph, &elements)
                finalizeBulletList(&bulletItems, &inBulletList, &elements)
                finalizeCheckboxList(&checkboxItems, &inCheckboxList, &elements)
                elements.append(MarkdownElement(type: .heading1, text: String(trimmedLine.dropFirst(2))))
                continue
            } else if trimmedLine.hasPrefix("## ") {
                finalizeParagraph(&currentParagraph, &elements)
                finalizeBulletList(&bulletItems, &inBulletList, &elements)
                finalizeCheckboxList(&checkboxItems, &inCheckboxList, &elements)
                elements.append(MarkdownElement(type: .heading2, text: String(trimmedLine.dropFirst(3))))
                continue
            } else if trimmedLine.hasPrefix("### ") {
                finalizeParagraph(&currentParagraph, &elements)
                finalizeBulletList(&bulletItems, &inBulletList, &elements)
                finalizeCheckboxList(&checkboxItems, &inCheckboxList, &elements)
                elements.append(MarkdownElement(type: .heading3, text: String(trimmedLine.dropFirst(4))))
                continue
            }
            
            // Handle bullet lists and checkboxes
            if trimmedLine.hasPrefix("• ") || trimmedLine.hasPrefix("- ") {
                finalizeParagraph(&currentParagraph, &elements)
                finalizeBulletList(&bulletItems, &inBulletList, &elements)
                finalizeCheckboxList(&checkboxItems, &inCheckboxList, &elements)
                if !inBulletList {
                    inBulletList = true
                }
                let bulletText = trimmedLine.hasPrefix("• ") ? String(trimmedLine.dropFirst(2)) : String(trimmedLine.dropFirst(2))
                bulletItems.append(bulletText)
                continue
            } else if trimmedLine.hasPrefix("☐ ") || trimmedLine.hasPrefix("□ ") || trimmedLine.hasPrefix("☑ ") || trimmedLine.hasPrefix("✓ ") || 
                      trimmedLine.hasPrefix("- [ ] ") || trimmedLine.hasPrefix("- [x] ") || trimmedLine.hasPrefix("- [X] ") {
                finalizeParagraph(&currentParagraph, &elements)
                finalizeBulletList(&bulletItems, &inBulletList, &elements)
                finalizeCheckboxList(&checkboxItems, &inCheckboxList, &elements)
                
                // Parse checkbox
                let isChecked: Bool
                let text: String
                
                if trimmedLine.hasPrefix("☐ ") || trimmedLine.hasPrefix("□ ") {
                    isChecked = false
                    text = String(trimmedLine.dropFirst(2))
                } else if trimmedLine.hasPrefix("☑ ") || trimmedLine.hasPrefix("✓ ") {
                    isChecked = true
                    text = String(trimmedLine.dropFirst(2))
                } else if trimmedLine.hasPrefix("- [ ] ") {
                    isChecked = false
                    text = String(trimmedLine.dropFirst(6))
                } else {
                    isChecked = true
                    text = String(trimmedLine.dropFirst(6))
                }
                
                let checkboxItem = CheckboxItem(text: text, isChecked: isChecked)
                if !inCheckboxList {
                    inCheckboxList = true
                }
                checkboxItems.append(checkboxItem)
                continue
            } else if inBulletList && !trimmedLine.isEmpty {
                // Continue previous bullet item
                if !bulletItems.isEmpty {
                    bulletItems[bulletItems.count - 1] += " " + trimmedLine
                }
                continue
            } else if inCheckboxList && !trimmedLine.isEmpty && 
                      !trimmedLine.hasPrefix("☐ ") && !trimmedLine.hasPrefix("□ ") && 
                      !trimmedLine.hasPrefix("☑ ") && !trimmedLine.hasPrefix("✓ ") &&
                      !trimmedLine.hasPrefix("- [ ] ") && !trimmedLine.hasPrefix("- [x] ") && !trimmedLine.hasPrefix("- [X] ") {
                // Continue previous checkbox item
                if !checkboxItems.isEmpty {
                    let lastIndex = checkboxItems.count - 1
                    let updatedText = checkboxItems[lastIndex].text + " " + trimmedLine
                    checkboxItems[lastIndex] = CheckboxItem(text: updatedText, isChecked: checkboxItems[lastIndex].isChecked)
                }
                continue
            }
            
            // Handle table rows
            if trimmedLine.hasPrefix("|") && trimmedLine.hasSuffix("|") {
                finalizeParagraph(&currentParagraph, &elements)
                finalizeBulletList(&bulletItems, &inBulletList, &elements)
                finalizeCheckboxList(&checkboxItems, &inCheckboxList, &elements)
                let cells = trimmedLine.components(separatedBy: "|").map { $0.trimmingCharacters(in: .whitespaces) }.filter { !$0.isEmpty }
                if !cells.isEmpty {
                    tableRows.append(cells)
                    inTable = true
                }
                continue
            } else if inTable {
                if !tableRows.isEmpty {
                    elements.append(MarkdownElement(type: .table, text: "", tableRows: tableRows))
                    tableRows = []
                }
                inTable = false
            }
            
            // Handle empty lines
            if trimmedLine.isEmpty {
                finalizeParagraph(&currentParagraph, &elements)
                finalizeBulletList(&bulletItems, &inBulletList, &elements)
                finalizeCheckboxList(&checkboxItems, &inCheckboxList, &elements)
                continue
            }
            
            // Regular paragraph text
            if !currentParagraph.isEmpty {
                currentParagraph += " "
            }
            currentParagraph += trimmedLine
        }
        
        // Finalize any remaining content
        finalizeParagraph(&currentParagraph, &elements)
        finalizeBulletList(&bulletItems, &inBulletList, &elements)
        finalizeCheckboxList(&checkboxItems, &inCheckboxList, &elements)
        
        if inTable && !tableRows.isEmpty {
            elements.append(MarkdownElement(type: .table, text: "", tableRows: tableRows))
        }
        
        return elements
    }
    
    private func finalizeParagraph(_ paragraph: inout String, _ elements: inout [MarkdownElement]) {
        if !paragraph.isEmpty {
            elements.append(MarkdownElement(type: .paragraph, text: paragraph))
            paragraph = ""
        }
    }
    
    private func finalizeBulletList(_ items: inout [String], _ inList: inout Bool, _ elements: inout [MarkdownElement]) {
        if inList && !items.isEmpty {
            elements.append(MarkdownElement(type: .bulletList, text: "", listItems: items))
            items = []
            inList = false
        }
    }
    
    private func finalizeCheckboxList(_ items: inout [CheckboxItem], _ inList: inout Bool, _ elements: inout [MarkdownElement]) {
        if inList && !items.isEmpty {
            elements.append(MarkdownElement(type: .checkboxList, text: "", checkboxItems: items))
            items = []
            inList = false
        }
    }
    
    private func parseInlineMarkdown(_ text: String) -> AttributedString {
        var attributedString = AttributedString(text)
        
        // Handle bold text **text**
        let boldPattern = #"\*\*(.*?)\*\*"#
        if let regex = try? NSRegularExpression(pattern: boldPattern) {
            let matches = regex.matches(in: text, range: NSRange(location: 0, length: text.count))
            for match in matches.reversed() {
                if let range = Range(match.range(at: 1), in: text) {
                    let boldText = String(text[range])
                    if let attributedRange = attributedString.range(of: "**\(boldText)**") {
                        attributedString.replaceSubrange(attributedRange, with: AttributedString(boldText))
                        if let newRange = attributedString.range(of: boldText) {
                            attributedString[newRange].font = .body.bold()
                        }
                    }
                }
            }
        }
        
        return attributedString
    }
}

// MARK: - Markdown Element Model
struct CheckboxItem {
    let id = UUID()
    let text: String
    let isChecked: Bool
}

struct MarkdownElement {
    let id = UUID()
    let type: MarkdownType
    let text: String
    let listItems: [String]
    let checkboxItems: [CheckboxItem]
    let tableRows: [[String]]
    
    init(type: MarkdownType, text: String, listItems: [String] = [], checkboxItems: [CheckboxItem] = [], tableRows: [[String]] = []) {
        self.type = type
        self.text = text
        self.listItems = listItems
        self.checkboxItems = checkboxItems
        self.tableRows = tableRows
    }
}

enum MarkdownType {
    case heading1, heading2, heading3
    case paragraph, bold
    case bulletList, checkboxList
    case codeBlock
    case table
    case separator
}

// MARK: - Profile View Implementation
struct ProfileView: View {
    @EnvironmentObject private var profileManager: ProfileManager
    @State private var showingGoalEditor = false
    @State private var editingGoal: Goal?
    @State private var showingPersonalInfoEditor = false
    @State private var showingCareerInfoEditor = false
    
    var body: some View {
        NavigationView {
            ZStack {
                // Pure black background
                Color(red: 0, green: 0, blue: 0)
                    .ignoresSafeArea()
                
                ScrollView(.vertical, showsIndicators: true) {
                    VStack(spacing: 20) {
                        // Header
                        profileHeader
                        
                        // Personal Info Section
                        personalInfoSection
                        
                        // Preferences Section
                        preferencesSection
                        
                        // Notifications Section
                        notificationSection
                        
                        // Career Info Section
                        careerInfoSection
                        
                        // Goals Section
                        goalsSection
                        
                        // Extra bottom padding
                        Spacer()
                            .frame(height: 100)
                    }
                    .padding(.horizontal, 16)
                }
                .scrollIndicators(.visible)
            }
            .navigationTitle("")
            .navigationBarTitleDisplayMode(.inline)
        }
        .sheet(isPresented: $showingPersonalInfoEditor) {
            PersonalInfoEditor(personalInfo: $profileManager.userProfile.personalInfo, profileManager: profileManager)
        }
        .sheet(isPresented: $showingCareerInfoEditor) {
            CareerInfoEditor(careerInfo: $profileManager.userProfile.careerInfo, profileManager: profileManager)
        }
        .sheet(isPresented: $showingGoalEditor) {
            GoalEditor(goal: editingGoal, profileManager: profileManager) {
                showingGoalEditor = false
                editingGoal = nil
            }
        }
    }
    
    // MARK: - Profile Header
    private var profileHeader: some View {
        VStack(spacing: 12) {
            // Profile Image Placeholder
            Circle()
                .fill(Color.orange)
                .frame(width: 80, height: 80)
                .overlay(
                    Text(profileManager.userProfile.personalInfo.name.isEmpty ? "👤" : String(profileManager.userProfile.personalInfo.name.prefix(1)).uppercased())
                        .font(.title)
                        .fontWeight(.bold)
                        .foregroundColor(.white)
                )
            
            VStack(spacing: 4) {
                Text(profileManager.userProfile.personalInfo.name.isEmpty ? "Setup Your Profile" : profileManager.userProfile.personalInfo.name)
                    .font(.title2)
                    .fontWeight(.bold)
                    .foregroundColor(.white)
                
                Text(profileManager.userProfile.personalInfo.currentJobTitle.isEmpty ? "Tap to add job title" : profileManager.userProfile.personalInfo.currentJobTitle)
                    .font(.subheadline)
                    .foregroundColor(.white.opacity(0.7))
                
                HStack(spacing: 4) {
                    Image(systemName: "briefcase.fill")
                        .foregroundColor(.orange)
                    Text("\(profileManager.userProfile.personalInfo.yearsOfExperience) years experience")
                        .font(.caption)
                        .foregroundColor(.white.opacity(0.6))
                }
            }
        }
        .padding(.top, 20)
    }
    
    // MARK: - Personal Info Section
    private var personalInfoSection: some View {
        ProfileSection(title: "Personal Info", icon: "person.fill") {
            Button(action: { showingPersonalInfoEditor = true }) {
                VStack(spacing: 8) {
                    InfoRow(label: "Name", value: profileManager.userProfile.personalInfo.name.isEmpty ? "Not set" : profileManager.userProfile.personalInfo.name)
                    InfoRow(label: "Age", value: "\(profileManager.userProfile.personalInfo.age)")
                    InfoRow(label: "Experience", value: "\(profileManager.userProfile.personalInfo.yearsOfExperience) years")
                    InfoRow(label: "Industry", value: profileManager.userProfile.personalInfo.industry.isEmpty ? "Not set" : profileManager.userProfile.personalInfo.industry)
                    InfoRow(label: "Location", value: profileManager.userProfile.personalInfo.location.isEmpty ? "Not set" : profileManager.userProfile.personalInfo.location)
                }
            }
            .buttonStyle(PlainButtonStyle())
        }
    }
    
    // MARK: - Preferences Section
    private var preferencesSection: some View {
        ProfileSection(title: "App Preferences", icon: "gear.fill") {
            VStack(spacing: 16) {
                // Theme Selection
                PreferenceSelector(
                    title: "Theme",
                    selection: Binding(
                        get: { profileManager.userProfile.preferences.theme },
                        set: { newTheme in
                            profileManager.userProfile.preferences.theme = newTheme
                            profileManager.saveProfile()
                        }
                    ),
                    options: AppTheme.allCases,
                    getDisplayText: { $0.rawValue }
                )
                
                // Coaching Style
                PreferenceSelector(
                    title: "Coaching Style",
                    selection: Binding(
                        get: { profileManager.userProfile.preferences.coachingStyle },
                        set: { newStyle in
                            profileManager.userProfile.preferences.coachingStyle = newStyle
                            profileManager.saveProfile()
                        }
                    ),
                    options: CoachingStyle.allCases,
                    getDisplayText: { $0.rawValue }
                )
                
                // Task Intensity
                PreferenceSelector(
                    title: "Task Intensity",
                    selection: Binding(
                        get: { profileManager.userProfile.preferences.taskIntensity },
                        set: { newIntensity in
                            profileManager.userProfile.preferences.taskIntensity = newIntensity
                            profileManager.saveProfile()
                        }
                    ),
                    options: TaskIntensity.allCases,
                    getDisplayText: { $0.rawValue }
                )
                
                Text(profileManager.userProfile.preferences.taskIntensity.description)
                    .font(.caption)
                    .foregroundColor(.white.opacity(0.6))
                    .multilineTextAlignment(.leading)
            }
        }
    }
    
    // MARK: - Notification Section
    private var notificationSection: some View {
        ProfileSection(title: "Daily Schedule", icon: "clock.fill") {
            VStack(spacing: 12) {
                TimeSelector(
                    title: "Wake Up",
                    time: Binding(
                        get: { profileManager.userProfile.notifications.wakeUpTime },
                        set: { newTime in
                            profileManager.userProfile.notifications.wakeUpTime = newTime
                            profileManager.saveProfile()
                        }
                    )
                )
                
                TimeSelector(
                    title: "Mid-Day Check-in",
                    time: Binding(
                        get: { profileManager.userProfile.notifications.midDayCheckIn },
                        set: { newTime in
                            profileManager.userProfile.notifications.midDayCheckIn = newTime
                            profileManager.saveProfile()
                        }
                    )
                )
                
                TimeSelector(
                    title: "Afternoon Wrap",
                    time: Binding(
                        get: { profileManager.userProfile.notifications.afternoonWrap },
                        set: { newTime in
                            profileManager.userProfile.notifications.afternoonWrap = newTime
                            profileManager.saveProfile()
                        }
                    )
                )
                
                TimeSelector(
                    title: "Goodnight",
                    time: Binding(
                        get: { profileManager.userProfile.notifications.goodnightTime },
                        set: { newTime in
                            profileManager.userProfile.notifications.goodnightTime = newTime
                            profileManager.saveProfile()
                        }
                    )
                )
                
                Toggle("Enable Notifications", isOn: Binding(
                    get: { profileManager.userProfile.notifications.enableNotifications },
                    set: { enabled in
                        profileManager.userProfile.notifications.enableNotifications = enabled
                        profileManager.saveProfile()
                    }
                ))
                .foregroundColor(.white)
            }
        }
    }
    
    // MARK: - Career Info Section
    private var careerInfoSection: some View {
        ProfileSection(title: "Career Journey", icon: "briefcase.fill") {
            Button(action: { showingCareerInfoEditor = true }) {
                VStack(spacing: 8) {
                    InfoRow(label: "Status", value: profileManager.userProfile.careerInfo.jobSearchStatus.rawValue)
                    
                    if let prevJob = profileManager.userProfile.careerInfo.previousJob {
                        InfoRow(label: "Previous Role", value: "\(prevJob.title) at \(prevJob.company)")
                    } else {
                        InfoRow(label: "Previous Role", value: "Not set")
                    }
                    
                    if let targetJob = profileManager.userProfile.careerInfo.targetJob {
                        InfoRow(label: "Target Role", value: "\(targetJob.title) at \(targetJob.company)")
                    } else {
                        InfoRow(label: "Target Role", value: "Not set")
                    }
                    
                    InfoRow(label: "LinkedIn", value: profileManager.userProfile.careerInfo.linkedInProfile.isEmpty ? "Not connected" : "Connected")
                }
            }
            .buttonStyle(PlainButtonStyle())
        }
    }
    
    // MARK: - Goals Section
    private var goalsSection: some View {
        ProfileSection(title: "Goals", icon: "target") {
            VStack(spacing: 12) {
                // Add Goal Button
                Button(action: {
                    editingGoal = nil
                    showingGoalEditor = true
                }) {
                    HStack {
                        Image(systemName: "plus.circle.fill")
                            .foregroundColor(.orange)
                        Text("Add New Goal")
                            .font(.system(size: 16, weight: .medium))
                            .foregroundColor(.white)
                        Spacer()
                    }
                    .padding()
                    .background(Color.white.opacity(0.1))
                    .cornerRadius(12)
                }
                .buttonStyle(PlainButtonStyle())
                
                // Goals List
                ForEach(profileManager.userProfile.goals) { goal in
                    GoalCard(goal: goal) {
                        editingGoal = goal
                        showingGoalEditor = true
                    }
                }
            }
        }
    }
}

// MARK: - Supporting Views
struct ProfileSection<Content: View>: View {
    let title: String
    let icon: String
    let content: Content
    
    init(title: String, icon: String, @ViewBuilder content: () -> Content) {
        self.title = title
        self.icon = icon
        self.content = content()
    }
    
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack(spacing: 8) {
                Image(systemName: icon)
                    .foregroundColor(.orange)
                    .font(.system(size: 16, weight: .medium))
                Text(title)
                    .font(.system(size: 18, weight: .semibold))
                    .foregroundColor(.white)
                Spacer()
            }
            
            content
        }
        .padding(16)
        .background(Color.white.opacity(0.05))
        .cornerRadius(12)
    }
}

struct InfoRow: View {
    let label: String
    let value: String
    
    var body: some View {
        HStack {
            Text(label)
                .font(.system(size: 14, weight: .medium))
                .foregroundColor(.white.opacity(0.7))
            Spacer()
            Text(value)
                .font(.system(size: 14))
                .foregroundColor(.white)
                .multilineTextAlignment(.trailing)
        }
    }
}

struct PreferenceSelector<T: CaseIterable & Hashable>: View where T.AllCases.Element == T {
    let title: String
    @Binding var selection: T
    let options: T.AllCases
    let getDisplayText: (T) -> String
    
    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(title)
                .font(.system(size: 14, weight: .medium))
                .foregroundColor(.white.opacity(0.7))
            
            ScrollView(.horizontal, showsIndicators: false) {
                HStack(spacing: 8) {
                    ForEach(Array(options), id: \.self) { option in
                        Button(action: { selection = option }) {
                            Text(getDisplayText(option))
                                .font(.system(size: 12, weight: .medium))
                                .foregroundColor(selection == option ? .black : .white)
                                .padding(.horizontal, 12)
                                .padding(.vertical, 6)
                                .background(selection == option ? .orange : Color.white.opacity(0.1))
                                .cornerRadius(8)
                        }
                    }
                }
                .padding(.horizontal, 2)
            }
        }
    }
}

struct TimeSelector: View {
    let title: String
    @Binding var time: Date
    
    var body: some View {
        HStack {
            Text(title)
                .font(.system(size: 14, weight: .medium))
                .foregroundColor(.white.opacity(0.7))
            Spacer()
            DatePicker("", selection: $time, displayedComponents: .hourAndMinute)
                .labelsHidden()
                .colorScheme(.dark)
        }
    }
}

struct GoalCard: View {
    let goal: Goal
    let onTap: () -> Void
    
    var body: some View {
        Button(action: onTap) {
            HStack(alignment: .top, spacing: 12) {
                VStack {
                    Circle()
                        .fill(goal.priority.color)
                        .frame(width: 8, height: 8)
                    Rectangle()
                        .fill(goal.priority.color.opacity(0.3))
                        .frame(width: 2)
                        .frame(maxHeight: .infinity)
                }
                
                VStack(alignment: .leading, spacing: 4) {
                    Text(goal.title)
                        .font(.system(size: 16, weight: .medium))
                        .foregroundColor(.white)
                        .multilineTextAlignment(.leading)
                    
                    if !goal.description.isEmpty {
                        Text(goal.description)
                            .font(.system(size: 14))
                            .foregroundColor(.white.opacity(0.7))
                            .multilineTextAlignment(.leading)
                    }
                    
                    HStack {
                        Text(goal.category.rawValue)
                            .font(.system(size: 12, weight: .medium))
                            .foregroundColor(.orange)
                            .padding(.horizontal, 8)
                            .padding(.vertical, 2)
                            .background(Color.orange.opacity(0.2))
                            .cornerRadius(6)
                        
                        if let targetDate = goal.targetDate {
                            Text(targetDate, style: .date)
                                .font(.caption)
                                .foregroundColor(.white.opacity(0.6))
                        }
                        
                        Spacer()
                        
                        if goal.isCompleted {
                            Image(systemName: "checkmark.circle.fill")
                                .foregroundColor(.green)
                        }
                    }
                }
                
                Spacer()
            }
            .padding(12)
            .background(Color.white.opacity(0.05))
            .cornerRadius(8)
        }
        .buttonStyle(PlainButtonStyle())
    }
}

// MARK: - Editor Views
struct PersonalInfoEditor: View {
    @Binding var personalInfo: PersonalInfo
    let profileManager: ProfileManager
    @Environment(\.dismiss) private var dismiss
    
    var body: some View {
        NavigationView {
            ZStack {
                Color(red: 0, green: 0, blue: 0).ignoresSafeArea()
                
                Form {
                    Section("Basic Information") {
                        TextField("Full Name", text: $personalInfo.name)
                        Stepper("Age: \(personalInfo.age)", value: $personalInfo.age, in: 18...99)
                        Stepper("Years of Experience: \(personalInfo.yearsOfExperience)", value: $personalInfo.yearsOfExperience, in: 0...50)
                    }
                    
                    Section("Professional Details") {
                        TextField("Current Job Title", text: $personalInfo.currentJobTitle)
                        TextField("Industry", text: $personalInfo.industry)
                        TextField("Location", text: $personalInfo.location)
                    }
                }
                .scrollContentBackground(.hidden)
                .foregroundColor(.white)
            }
            .navigationTitle("Personal Info")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarLeading) {
                    Button("Cancel") { dismiss() }
                        .foregroundColor(.white)
                }
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button("Save") {
                        profileManager.updatePersonalInfo(personalInfo)
                        dismiss()
                    }
                    .foregroundColor(.orange)
                }
            }
        }
    }
}

struct CareerInfoEditor: View {
    @Binding var careerInfo: CareerInfo
    let profileManager: ProfileManager
    @Environment(\.dismiss) private var dismiss
    
    var body: some View {
        NavigationView {
            ZStack {
                Color(red: 0, green: 0, blue: 0).ignoresSafeArea()
                
                Form {
                    Section("Job Search Status") {
                        Picker("Status", selection: $careerInfo.jobSearchStatus) {
                            ForEach(JobSearchStatus.allCases, id: \.self) { status in
                                Text(status.rawValue).tag(status)
                            }
                        }
                    }
                    
                    Section("Previous Role") {
                        TextField("Job Title", text: Binding(
                            get: { careerInfo.previousJob?.title ?? "" },
                            set: { newValue in
                                if careerInfo.previousJob == nil {
                                    careerInfo.previousJob = JobInfo()
                                }
                                careerInfo.previousJob?.title = newValue
                            }
                        ))
                        TextField("Company", text: Binding(
                            get: { careerInfo.previousJob?.company ?? "" },
                            set: { newValue in
                                if careerInfo.previousJob == nil {
                                    careerInfo.previousJob = JobInfo()
                                }
                                careerInfo.previousJob?.company = newValue
                            }
                        ))
                    }
                    
                    Section("Target Role") {
                        TextField("Job Title", text: Binding(
                            get: { careerInfo.targetJob?.title ?? "" },
                            set: { newValue in
                                if careerInfo.targetJob == nil {
                                    careerInfo.targetJob = JobInfo()
                                }
                                careerInfo.targetJob?.title = newValue
                            }
                        ))
                        TextField("Company", text: Binding(
                            get: { careerInfo.targetJob?.company ?? "" },
                            set: { newValue in
                                if careerInfo.targetJob == nil {
                                    careerInfo.targetJob = JobInfo()
                                }
                                careerInfo.targetJob?.company = newValue
                            }
                        ))
                    }
                    
                    Section("Professional Links") {
                        TextField("LinkedIn Profile URL", text: $careerInfo.linkedInProfile)
                        TextField("Portfolio URL", text: $careerInfo.portfolioURL)
                    }
                }
                .scrollContentBackground(.hidden)
                .foregroundColor(.white)
            }
            .navigationTitle("Career Info")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarLeading) {
                    Button("Cancel") { dismiss() }
                        .foregroundColor(.white)
                }
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button("Save") {
                        profileManager.updateCareerInfo(careerInfo)
                        dismiss()
                    }
                    .foregroundColor(.orange)
                }
            }
        }
    }
}

struct GoalEditor: View {
    let goal: Goal?
    let profileManager: ProfileManager
    let onDismiss: () -> Void
    
    @State private var title = ""
    @State private var description = ""
    @State private var category: GoalCategory = .career
    @State private var priority: GoalPriority = .medium
    @State private var targetDate: Date = Date()
    @State private var hasTargetDate = false
    @State private var isCompleted = false
    
    var body: some View {
        NavigationView {
            ZStack {
                Color(red: 0, green: 0, blue: 0).ignoresSafeArea()
                
                Form {
                    Section("Goal Details") {
                        TextField("Goal Title", text: $title)
                        TextField("Description", text: $description, axis: .vertical)
                            .lineLimit(3...6)
                    }
                    
                    Section("Category & Priority") {
                        Picker("Category", selection: $category) {
                            ForEach(GoalCategory.allCases, id: \.self) { cat in
                                Text(cat.rawValue).tag(cat)
                            }
                        }
                        
                        Picker("Priority", selection: $priority) {
                            ForEach(GoalPriority.allCases, id: \.self) { pri in
                                Text(pri.rawValue).tag(pri)
                            }
                        }
                    }
                    
                    Section("Timeline") {
                        Toggle("Set Target Date", isOn: $hasTargetDate)
                        
                        if hasTargetDate {
                            DatePicker("Target Date", selection: $targetDate, displayedComponents: .date)
                        }
                    }
                    
                    if goal != nil {
                        Section("Status") {
                            Toggle("Completed", isOn: $isCompleted)
                        }
                    }
                }
                .scrollContentBackground(.hidden)
                .foregroundColor(.white)
            }
            .navigationTitle(goal == nil ? "New Goal" : "Edit Goal")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarLeading) {
                    Button("Cancel") { onDismiss() }
                        .foregroundColor(.white)
                }
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button("Save") {
                        let newGoal = Goal(
                            title: title,
                            description: description,
                            category: category,
                            targetDate: hasTargetDate ? targetDate : nil,
                            isCompleted: isCompleted,
                            priority: priority
                        )
                        
                        if let existingGoal = goal {
                            // Update existing goal with same ID
                            var updatedGoal = newGoal
                            // Copy the ID from existing goal
                            profileManager.updateGoal(updatedGoal)
                        } else {
                            profileManager.addGoal(newGoal)
                        }
                        
                        onDismiss()
                    }
                    .foregroundColor(.orange)
                }
            }
        }
        .onAppear {
            if let goal = goal {
                title = goal.title
                description = goal.description
                category = goal.category
                priority = goal.priority
                isCompleted = goal.isCompleted
                if let date = goal.targetDate {
                    targetDate = date
                    hasTargetDate = true
                }
            }
        }
    }
}

// MARK: - Embedded AI Message Generator
struct AIGeneratorEmbeddedView: View {
    @State private var intensity: Double = 50
    @State private var languageClean: Double = 50
    @State private var humorStyle: Double = 50
    @State private var actionOrientation: Double = 50
    @State private var messageLength: Double = 50
    @State private var musicStyle: Double = 50
    @State private var visualStyle: Double = 50
    
    @State private var userInput: String = ""
    @State private var generatedMessage: String = ""
    @State private var isGenerating: Bool = false
    @State private var messageStyle: String = ""
    
    var body: some View {
        NavigationView {
            ZStack {
                Color.black.ignoresSafeArea()
                
                ScrollView {
                    VStack(spacing: 20) {
                        // Header
                        VStack(spacing: 8) {
                            Image(systemName: "brain.head.profile")
                                .font(.system(size: 50))
                                .foregroundColor(.orange)
                            
                            Text("AI Message Generator")
                                .font(.title)
                                .fontWeight(.bold)
                                .foregroundColor(.white)
                            
                            Text("Customize your perfect motivational message")
                                .font(.subheadline)
                                .foregroundColor(.gray)
                        }
                        .padding(.top)
                        
                        // User Input
                        VStack(alignment: .leading, spacing: 8) {
                            Text("What do you need motivation for?")
                                .font(.headline)
                                .foregroundColor(.white)
                            
                            TextField("e.g., waking up early, starting a workout routine...", text: $userInput, axis: .vertical)
                                .textFieldStyle(RoundedBorderTextFieldStyle())
                                .lineLimit(3...6)
                        }
                        .padding(.horizontal)
                        
                        // Slider Controls
                        VStack(spacing: 20) {
                            EmbeddedSliderRow(title: "Intensity", value: $intensity, 
                                    leftLabel: "😌 Chill", rightLabel: "💪 Drill Sergeant")
                            
                            EmbeddedSliderRow(title: "Language Style", value: $languageClean,
                                    leftLabel: "🤬 Raw", rightLabel: "😇 Clean")
                            
                            EmbeddedSliderRow(title: "Humor Level", value: $humorStyle,
                                    leftLabel: "😐 Serious", rightLabel: "😂 Funny")
                            
                            EmbeddedSliderRow(title: "Approach", value: $actionOrientation,
                                    leftLabel: "🧘 Mindful", rightLabel: "⚡ Action")
                            
                            EmbeddedSliderRow(title: "Message Length", value: $messageLength,
                                    leftLabel: "💬 Quote", rightLabel: "📜 Speech")
                            
                            EmbeddedSliderRow(title: "Music Style", value: $musicStyle,
                                    leftLabel: "🎵 Chill", rightLabel: "🎸 Rock")
                            
                            EmbeddedSliderRow(title: "Visual Style", value: $visualStyle,
                                    leftLabel: "🖼️ Still", rightLabel: "🎬 Video")
                        }
                        .padding(.horizontal)
                        
                        // Generate Button
                        Button(action: generateMessage) {
                            HStack {
                                if isGenerating {
                                    ProgressView()
                                        .progressViewStyle(CircularProgressViewStyle(tint: .white))
                                        .scaleEffect(0.8)
                                    Text("Generating...")
                                } else {
                                    Image(systemName: "sparkles")
                                    Text("Generate My Message")
                                }
                            }
                            .frame(maxWidth: .infinity)
                            .padding()
                            .background(userInput.isEmpty ? Color.gray : Color.orange)
                            .foregroundColor(.white)
                            .cornerRadius(10)
                            .font(.headline)
                        }
                        .disabled(userInput.isEmpty || isGenerating)
                        .padding(.horizontal)
                        
                        // Generated Message Display
                        if !generatedMessage.isEmpty {
                            VStack(alignment: .leading, spacing: 12) {
                                Text("Your Personalized Message")
                                    .font(.headline)
                                    .foregroundColor(.white)
                                    .padding(.horizontal)
                                
                                VStack(spacing: 12) {
                                    Text(generatedMessage)
                                        .padding()
                                        .background(Color(.systemGray6))
                                        .cornerRadius(12)
                                        .font(.body)
                                        .lineSpacing(4)
                                    
                                    HStack {
                                        VStack {
                                            Text("Style")
                                                .font(.caption)
                                                .foregroundColor(.secondary)
                                            Text(messageStyle.capitalized)
                                                .font(.caption2)
                                                .fontWeight(.semibold)
                                                .foregroundColor(.white)
                                        }
                                        
                                        Spacer()
                                        
                                        VStack {
                                            Text("Intensity")
                                                .font(.caption)
                                                .foregroundColor(.secondary)
                                            Text("\(Int(intensity))%")
                                                .font(.caption2)
                                                .fontWeight(.semibold)
                                                .foregroundColor(.white)
                                        }
                                        
                                        Spacer()
                                        
                                        VStack {
                                            Text("Length")
                                                .font(.caption)
                                                .foregroundColor(.secondary)
                                            Text(messageLength > 50 ? "Long" : "Short")
                                                .font(.caption2)
                                                .fontWeight(.semibold)
                                                .foregroundColor(.white)
                                        }
                                    }
                                    .padding(.horizontal, 8)
                                }
                                .padding(.horizontal)
                            }
                        }
                        
                        Spacer(minLength: 20)
                    }
                }
            }
            .navigationBarHidden(true)
        }
        .preferredColorScheme(.dark)
    }
    
    private func generateMessage() {
        guard !userInput.isEmpty else { return }
        
        isGenerating = true
        
        DispatchQueue.main.asyncAfter(deadline: .now() + 1.5) {
            let style = determineMessageStyle()
            messageStyle = style
            generatedMessage = createMessage(style: style, topic: userInput)
            isGenerating = false
        }
    }
    
    private func determineMessageStyle() -> String {
        if intensity > 80 {
            return languageClean < 30 ? "Ultra Intense" : "Drill Sergeant"
        } else if intensity < 30 {
            return "Zen & Mindful"
        } else if humorStyle > 60 {
            return languageClean > 70 ? "Motivational Comedy" : "Raw Comedy"
        } else {
            return "Rise & Grind"
        }
    }
    
    private func createMessage(style: String, topic: String) -> String {
        let templates = [
            "Ultra Intense": "🔥 TIME TO ABSOLUTELY DOMINATE \(topic.uppercased())! No excuses, no delays, just pure RELENTLESS ACTION! Your future self is watching - make them proud!",
            
            "Drill Sergeant": "⚡ LISTEN UP! \(topic.capitalized) isn't just a goal - it's your MISSION! Stop making excuses and START MAKING MOVES! Discipline equals freedom!",
            
            "Zen & Mindful": "🧘‍♀️ Take a deep breath and center yourself. Your journey with \(topic) is unfolding perfectly. Trust the process, honor your growth, and remember - every step forward is sacred progress.",
            
            "Motivational Comedy": "😂 So you want to master \(topic)? That's like trying to fold a fitted sheet while riding a unicycle - seems impossible, but hey, at least you'll have some interesting stories to tell! You've got this!",
            
            "Raw Comedy": "😄 Alright, let's talk about \(topic). It's tough, it's going to kick your butt, but you know what? You're tougher! Time to show \(topic) who's boss!",
            
            "Rise & Grind": "💪 TODAY IS THE DAY you take control of \(topic)! No more 'tomorrow' - no more 'when I'm ready' - TODAY is when you start building the life you deserve! Let's GO!"
        ]
        
        return templates[style] ?? "🚀 You've got this! \(topic.capitalized) is just another challenge to conquer. Believe in yourself and take that first step!"
    }
}

// MARK: - Supporting Views for AI Generator
struct EmbeddedSliderRow: View {
    let title: String
    @Binding var value: Double
    let leftLabel: String
    let rightLabel: String
    
    var body: some View {
        VStack(spacing: 8) {
            HStack {
                Text(title)
                    .font(.subheadline)
                    .fontWeight(.medium)
                    .foregroundColor(.white)
                Spacer()
                Text("\(Int(value))")
                    .font(.subheadline)
                    .foregroundColor(.orange)
                    .fontWeight(.semibold)
            }
            
            HStack {
                Text(leftLabel)
                    .font(.caption)
                    .foregroundColor(.gray)
                Spacer()
                Text(rightLabel)
                    .font(.caption)
                    .foregroundColor(.gray)
            }
            
            Slider(value: $value, in: 0...100)
                .accentColor(.orange)
        }
    }
}

#Preview {
    ContentView()
}