import SwiftUI

struct AnimatedTextView: View {
    let fullText: String
    let animationSpeed: Double
    let backgroundImageName: String?
    
    @State private var displayedSentences: [String] = []
    @State private var currentSentenceIndex = 0
    @State private var isAnimating = false
    @State private var isPaused = false
    @State private var showControls = true
    @State private var animationTimer: Timer?
    
    private var textSentences: [String] {
        // Split text into sentences for dramatic effect
        let sentences = fullText.components(separatedBy: CharacterSet(charactersIn: ".!?"))
            .map { $0.trimmingCharacters(in: .whitespacesAndNewlines) }
            .filter { !$0.isEmpty }
        
        // Add punctuation back and ensure proper formatting
        return sentences.enumerated().map { index, sentence in
            let trimmed = sentence.trimmingCharacters(in: .whitespacesAndNewlines)
            if trimmed.isEmpty { return "" }
            
            // Add appropriate punctuation
            if index < sentences.count - 1 {
                return trimmed + "."
            } else {
                return trimmed + "!"
            }
        }.filter { !$0.isEmpty }
    }
    
    init(text: String, animationSpeed: Double = 2.5, backgroundImage: String? = nil) {
        self.fullText = text
        self.animationSpeed = animationSpeed
        self.backgroundImageName = backgroundImage
    }
    
    var body: some View {
        print("🎬 AnimatedTextView: Body is being called")
        return ZStack {
            // Background
            backgroundView
            
            // Main Content
            VStack(spacing: 0) {
                Spacer()
                
                // Animated Text Display
                animatedTextContent
                
                Spacer()
                
                // Controls (if visible)
                if showControls {
                    controlsView
                        .transition(.move(edge: .bottom).combined(with: .opacity))
                }
            }
        }
        .onAppear {
            print("🎬 AnimatedTextView: onAppear called, starting animation")
            startAnimation()
        }
        .onDisappear {
            print("🎬 AnimatedTextView: onDisappear called, stopping animation")
            stopAnimation()
        }
        .onTapGesture {
            withAnimation(.easeInOut(duration: 0.3)) {
                showControls.toggle()
            }
        }
    }
    
    private var backgroundView: some View {
        Group {
            if let backgroundImageName = backgroundImageName {
                // Use placeholder gradient since we don't have actual images
                backgroundGradient(for: backgroundImageName)
                    .ignoresSafeArea()
            } else {
                // Default gradient background
                LinearGradient(
                    gradient: Gradient(colors: [
                        Color.blue.opacity(0.8),
                        Color.purple.opacity(0.6),
                        Color.indigo.opacity(0.8)
                    ]),
                    startPoint: .topLeading,
                    endPoint: .bottomTrailing
                )
                .ignoresSafeArea()
            }
            
            // Dark overlay for text readability
            Color.black.opacity(0.4)
                .ignoresSafeArea()
        }
    }
    
    private var animatedTextContent: some View {
        ScrollView {
            VStack(alignment: .center, spacing: 16) {
                ForEach(Array(displayedSentences.enumerated()), id: \.offset) { index, sentence in
                    Text(sentence)
                        .font(.system(size: 24, weight: .bold, design: .default))
                        .foregroundColor(.white)
                        .shadow(color: .black, radius: 2, x: 1, y: 1)
                        .multilineTextAlignment(.center)
                        .padding(.horizontal, 20)
                        .opacity(1.0)
                        .scaleEffect(1.0)
                        .transition(.asymmetric(
                            insertion: .opacity.combined(with: .scale(scale: 0.7)).combined(with: .move(edge: .top)),
                            removal: .opacity
                        ))
                        .animation(.spring(response: 0.8, dampingFraction: 0.7), value: displayedSentences.count)
                }
            }
            .frame(maxWidth: .infinity)
            .padding(.vertical, 40)
        }
        .frame(maxHeight: 400)
    }
    
    private var controlsView: some View {
        HStack(spacing: 24) {
            // Restart Button
            Button(action: restartAnimation) {
                Image(systemName: "arrow.clockwise")
                    .font(.title2)
                    .foregroundColor(.white)
                    .frame(width: 50, height: 50)
                    .background(Color.black.opacity(0.3))
                    .clipShape(Circle())
            }
            
            // Play/Pause Button
            Button(action: togglePlayPause) {
                Image(systemName: isPaused ? "play.fill" : "pause.fill")
                    .font(.title2)
                    .foregroundColor(.white)
                    .frame(width: 50, height: 50)
                    .background(Color.black.opacity(0.3))
                    .clipShape(Circle())
            }
            
            // Speed Indicator
            VStack(spacing: 2) {
                Text("Speed")
                    .font(.caption)
                    .foregroundColor(.white)
                
                Text("\(animationSpeed, specifier: "%.1f")s")
                    .font(.caption2)
                    .foregroundColor(.white.opacity(0.8))
            }
        }
        .padding(.bottom, 40)
    }
    
    // MARK: - Animation Control
    private func startAnimation() {
        print("🎬 AnimatedTextView: startAnimation called")
        print("🎬 AnimatedTextView: textSentences count: \(textSentences.count)")
        print("🎬 AnimatedTextView: First sentence: \(textSentences.first ?? "nil")")
        
        guard !textSentences.isEmpty else { 
            print("🎬 AnimatedTextView: textSentences is empty, returning")
            return 
        }
        
        resetAnimation()
        isAnimating = true
        isPaused = false
        
        scheduleNextSentence()
    }
    
    private func scheduleNextSentence() {
        guard isAnimating && !isPaused && currentSentenceIndex < textSentences.count else {
            if currentSentenceIndex >= textSentences.count {
                isAnimating = false
            }
            return
        }
        
        animationTimer = Timer.scheduledTimer(withTimeInterval: animationSpeed, repeats: false) { _ in
            addNextSentence()
        }
    }
    
    private func addNextSentence() {
        guard currentSentenceIndex < textSentences.count else {
            print("🎬 AnimatedTextView: Animation complete, all sentences displayed")
            isAnimating = false
            return
        }
        
        print("🎬 AnimatedTextView: Adding sentence \(currentSentenceIndex): \(textSentences[currentSentenceIndex])")
        
        withAnimation(.spring(response: 0.8, dampingFraction: 0.7)) {
            displayedSentences.append(textSentences[currentSentenceIndex])
        }
        
        currentSentenceIndex += 1
        
        // Schedule next sentence
        scheduleNextSentence()
    }
    
    private func togglePlayPause() {
        isPaused.toggle()
        
        if !isPaused && isAnimating {
            scheduleNextSentence()
        } else {
            animationTimer?.invalidate()
        }
    }
    
    private func restartAnimation() {
        stopAnimation()
        
        withAnimation(.easeOut(duration: 0.5)) {
            displayedSentences = []
        }
        
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.6) {
            startAnimation()
        }
    }
    
    private func resetAnimation() {
        displayedSentences = []
        currentSentenceIndex = 0
    }
    
    private func stopAnimation() {
        isAnimating = false
        isPaused = false
        animationTimer?.invalidate()
        animationTimer = nil
    }
    
    // MARK: - Background Gradients
    private func backgroundGradient(for imageName: String) -> LinearGradient {
        switch imageName {
        case "mountain_sunrise":
            return LinearGradient(
                gradient: Gradient(colors: [Color.orange, Color.yellow, Color.pink]),
                startPoint: .topLeading,
                endPoint: .bottomTrailing
            )
        case "forest_river":
            return LinearGradient(
                gradient: Gradient(colors: [Color.green, Color.blue, Color.teal]),
                startPoint: .topLeading,
                endPoint: .bottomTrailing
            )
        case "golden_fields":
            return LinearGradient(
                gradient: Gradient(colors: [Color.yellow, Color.orange, Color.brown]),
                startPoint: .topLeading,
                endPoint: .bottomTrailing
            )
        case "canyon_vista":
            return LinearGradient(
                gradient: Gradient(colors: [Color.red, Color.orange, Color.yellow]),
                startPoint: .topLeading,
                endPoint: .bottomTrailing
            )
        case "starry_night":
            return LinearGradient(
                gradient: Gradient(colors: [Color.indigo, Color.purple, Color.black]),
                startPoint: .topLeading,
                endPoint: .bottomTrailing
            )
        default:
            return LinearGradient(
                gradient: Gradient(colors: [Color.blue, Color.purple, Color.indigo]),
                startPoint: .topLeading,
                endPoint: .bottomTrailing
            )
        }
    }
}

// MARK: - Extension for MotivationalMessage
extension AnimatedTextView {
    init(message: MotivationalMessage) {
        print("🎬 AnimatedTextView: Initializing with message: \(message.title)")
        print("🎬 AnimatedTextView: Message content: \(String(message.content.prefix(50)))...")
        self.init(
            text: message.content,
            animationSpeed: 2.5,
            backgroundImage: message.backgroundImageName
        )
    }
}

// MARK: - Preview
struct AnimatedTextView_Previews: PreviewProvider {
    static var previews: some View {
        AnimatedTextView(
            text: "WAKE THE F*CK UP, FUTURE CEO! Today's the day you turn rejection into REDIRECTION! Your dream job is out there RIGHT NOW wondering where the hell you are!",
            animationSpeed: 2.0,
            backgroundImage: "mountain_sunrise"
        )
    }
} 