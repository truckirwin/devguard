import SwiftUI

// MARK: - Three Ring View
struct ThreeRingView: View {
    let rings: [TaskProgressRing]
    
    var body: some View {
        HStack(spacing: 30) {
            ForEach(rings) { ring in
                ProgressRingView(ring: ring)
            }
        }
        .padding(.vertical, 16)
    }
}

// MARK: - Individual Progress Ring
struct ProgressRingView: View {
    let ring: TaskProgressRing
    @State private var animationProgress: Double = 0
    
    var body: some View {
        VStack(spacing: 8) {
            ZStack {
                // Background circle
                Circle()
                    .stroke(Color(ring.category.color).opacity(0.2), lineWidth: 8)
                    .frame(width: 80, height: 80)
                
                // Progress circle with gradient
                Circle()
                    .trim(from: 0, to: animationProgress)
                    .stroke(
                        LinearGradient(
                            colors: [Color(ring.category.color), Color(ring.category.color).opacity(0.7)],
                            startPoint: .topLeading,
                            endPoint: .bottomTrailing
                        ),
                        style: StrokeStyle(lineWidth: 8, lineCap: .round)
                    )
                    .frame(width: 80, height: 80)
                    .rotationEffect(.degrees(-90))
                    .animation(.easeInOut(duration: 0.8).delay(0.2), value: animationProgress)
                
                // Center text
                VStack(spacing: 2) {
                    Text("\(Int(ring.progress * 100))%")
                        .font(.system(size: 16, weight: .bold, design: .rounded))
                        .foregroundColor(.white)
                    
                    Text("\(ring.completedTasks)/\(ring.totalTasks)")
                        .font(.system(size: 10, weight: .medium))
                        .foregroundColor(.white.opacity(0.7))
                }
            }
            
            VStack(spacing: 4) {
                Text(ring.category.name)
                    .font(.system(size: 14, weight: .semibold))
                    .foregroundColor(.white)
                
                Text(ring.category.subtitle)
                    .font(.system(size: 10))
                    .foregroundColor(.white.opacity(0.6))
                    .multilineTextAlignment(.center)
            }
        }
        .onAppear {
            withAnimation(.easeInOut(duration: 0.8).delay(0.3)) {
                animationProgress = ring.progress
            }
        }
        .onChange(of: ring.progress) { newProgress in
            withAnimation(.easeInOut(duration: 0.5)) {
                animationProgress = newProgress
            }
        }
    }
}

// MARK: - Compact Progress Ring
struct CompactProgressRingView: View {
    let ring: TaskProgressRing
    @State private var animationProgress: Double = 0
    
    var body: some View {
        ZStack {
            // Background circle
            Circle()
                .stroke(Color(ring.category.color).opacity(0.2), lineWidth: 4)
                .frame(width: 40, height: 40)
            
            // Progress circle
            Circle()
                .trim(from: 0, to: animationProgress)
                .stroke(
                    Color(ring.category.color),
                    style: StrokeStyle(lineWidth: 4, lineCap: .round)
                )
                .frame(width: 40, height: 40)
                .rotationEffect(.degrees(-90))
                .animation(.easeInOut(duration: 0.5), value: animationProgress)
            
            // Center indicator
            if ring.targetMet {
                Image(systemName: "checkmark")
                    .font(.caption)
                    .foregroundColor(Color(ring.category.color))
                    .fontWeight(.bold)
            } else {
                Text("\(Int(ring.progress * 100))%")
                    .font(.caption2)
                    .fontWeight(.bold)
                    .foregroundColor(Color(ring.category.color))
            }
        }
        .onAppear {
            withAnimation(.easeInOut(duration: 0.5).delay(0.1)) {
                animationProgress = ring.progress
            }
        }
        .onChange(of: ring.progress) { newProgress in
            withAnimation(.easeInOut(duration: 0.3)) {
                animationProgress = newProgress
            }
        }
    }
}

// MARK: - Previews
#Preview("Three Ring View") {
    let rings = [
        TaskProgressRing(category: .hustle, completedTasks: 4, totalTasks: 5),
        TaskProgressRing(category: .grind, completedTasks: 2, totalTasks: 4),
        TaskProgressRing(category: .skills, completedTasks: 3, totalTasks: 3)
    ]
    
    ThreeRingView(rings: rings)
        .padding()
        .background(Color.black)
        .preferredColorScheme(.dark)
}

#Preview("Compact Ring View") {
    let ring = TaskProgressRing(category: .hustle, completedTasks: 2, totalTasks: 3)
    
    return CompactProgressRingView(ring: ring)
        .padding()
        .background(Color.black)
        .preferredColorScheme(.dark)
} 