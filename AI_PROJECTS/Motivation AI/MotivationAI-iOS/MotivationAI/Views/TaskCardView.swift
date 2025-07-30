import SwiftUI

struct TaskCardView: View {
    let task: DailyTask
    let onComplete: () -> Void
    let onSkip: () -> Void
    let onReset: () -> Void
    
    @State private var dragOffset: CGSize = .zero
    @State private var cardScale: CGFloat = 1.0
    @State private var isAnimating: Bool = false
    
    private let swipeThreshold: CGFloat = 100
    
    var body: some View {
        HStack(spacing: 12) {
            // Status indicator
            statusIndicator
            
            // Task content
            VStack(alignment: .leading, spacing: 4) {
                HStack {
                    Text(task.title)
                        .font(.subheadline)
                        .fontWeight(.semibold)
                        .foregroundColor(.primary)
                        .lineLimit(1)
                    
                    Spacer()
                    
                    // Difficulty indicator
                    HStack(spacing: 2) {
                        Image(systemName: task.difficulty.icon)
                            .font(.caption2)
                            .foregroundColor(Color(task.difficulty.color))
                        
                        Text(task.difficulty.rawValue)
                            .font(.caption2)
                            .foregroundColor(Color(task.difficulty.color))
                    }
                }
                
                Text(task.description)
                    .font(.caption)
                    .foregroundColor(.secondary)
                    .lineLimit(2)
                    .multilineTextAlignment(.leading)
                
                HStack {
                    // Category badge
                    HStack(spacing: 4) {
                        Image(systemName: task.category.icon)
                            .font(.caption2)
                        Text(task.category.rawValue)
                            .font(.caption2)
                    }
                    .foregroundColor(Color(task.category.color))
                    .padding(.horizontal, 8)
                    .padding(.vertical, 4)
                    .background(Color(task.category.color).opacity(0.1))
                    .cornerRadius(8)
                    
                    Spacer()
                    
                    // Estimated time
                    HStack(spacing: 2) {
                        Image(systemName: "clock")
                            .font(.caption2)
                        Text("\(task.estimatedTimeMinutes)m")
                            .font(.caption2)
                    }
                    .foregroundColor(.secondary)
                }
            }
            
            Spacer()
        }
        .padding(12)
        .background(cardBackground)
        .cornerRadius(12)
        .scaleEffect(cardScale)
        .offset(dragOffset)
        .opacity(task.isCompleted ? 0.7 : 1.0)
        .overlay(swipeIndicators)
        .gesture(swipeGesture)
        .animation(.spring(response: 0.6, dampingFraction: 0.8), value: dragOffset)
        .animation(.easeInOut(duration: 0.2), value: cardScale)
        .onTapGesture {
            if task.status == .pending {
                hapticFeedback()
                withAnimation(.spring(response: 0.4, dampingFraction: 0.6)) {
                    onComplete()
                }
            } else if task.status != .pending {
                hapticFeedback()
                withAnimation(.spring(response: 0.4, dampingFraction: 0.6)) {
                    onReset()
                }
            }
        }
    }
    
    private var statusIndicator: some View {
        ZStack {
            Circle()
                .fill(Color(task.status.color).opacity(0.2))
                .frame(width: 32, height: 32)
            
            Image(systemName: task.status.icon)
                .font(.system(size: 16, weight: .semibold))
                .foregroundColor(Color(task.status.color))
        }
        .scaleEffect(isAnimating ? 1.2 : 1.0)
        .animation(.easeInOut(duration: 0.3), value: isAnimating)
    }
    
    private var cardBackground: some View {
        RoundedRectangle(cornerRadius: 12)
            .fill(Color(.systemBackground))
            .shadow(color: .black.opacity(0.05), radius: 2, x: 0, y: 1)
            .overlay(
                RoundedRectangle(cornerRadius: 12)
                    .stroke(
                        task.isCompleted ? Color(task.category.color).opacity(0.3) : Color.clear,
                        lineWidth: task.isCompleted ? 2 : 0
                    )
            )
    }
    
    private var swipeIndicators: some View {
        HStack {
            // Left swipe indicator (Complete)
            if dragOffset.width > swipeThreshold / 2 {
                VStack {
                    Image(systemName: "checkmark.circle.fill")
                        .font(.title2)
                        .foregroundColor(.green)
                    Text("Complete")
                        .font(.caption)
                        .foregroundColor(.green)
                        .fontWeight(.semibold)
                }
                .opacity(min(1.0, dragOffset.width / swipeThreshold))
                .padding(.leading)
            }
            
            Spacer()
            
            // Right swipe indicator (Skip)
            if dragOffset.width < -swipeThreshold / 2 {
                VStack {
                    Image(systemName: "xmark.circle.fill")
                        .font(.title2)
                        .foregroundColor(.orange)
                    Text("Skip")
                        .font(.caption)
                        .foregroundColor(.orange)
                        .fontWeight(.semibold)
                }
                .opacity(min(1.0, -dragOffset.width / swipeThreshold))
                .padding(.trailing)
            }
        }
    }
    
    private var swipeGesture: some Gesture {
        DragGesture()
            .onChanged { value in
                // Only allow swipe if task is pending
                guard task.status == .pending else { return }
                
                dragOffset = value.translation
                
                // Scale effect during drag
                let dragMagnitude = sqrt(pow(value.translation.width, 2) + pow(value.translation.height, 2))
                cardScale = max(0.95, 1.0 - dragMagnitude / 1000)
            }
            .onEnded { value in
                guard task.status == .pending else { return }
                
                if value.translation.width > swipeThreshold {
                    // Complete task
                    hapticFeedback()
                    withAnimation(.spring(response: 0.4, dampingFraction: 0.6)) {
                        isAnimating = true
                        onComplete()
                    }
                    DispatchQueue.main.asyncAfter(deadline: .now() + 0.3) {
                        isAnimating = false
                    }
                } else if value.translation.width < -swipeThreshold {
                    // Skip task
                    hapticFeedback()
                    withAnimation(.spring(response: 0.4, dampingFraction: 0.6)) {
                        onSkip()
                    }
                }
                
                // Reset position and scale
                withAnimation(.spring(response: 0.6, dampingFraction: 0.8)) {
                    dragOffset = .zero
                    cardScale = 1.0
                }
            }
    }
    
    private func hapticFeedback() {
        let impact = UIImpactFeedbackGenerator(style: .medium)
        impact.impactOccurred()
    }
}

// MARK: - Quick Action Button
struct QuickActionButton: View {
    let title: String
    let subtitle: String
    let icon: String
    let color: Color
    let action: () -> Void
    
    var body: some View {
        Button(action: action) {
            VStack(spacing: 8) {
                Image(systemName: icon)
                    .font(.title2)
                    .foregroundColor(color)
                
                VStack(spacing: 2) {
                    Text(title)
                        .font(.system(size: 14, weight: .semibold))
                        .foregroundColor(.white)
                    
                    Text(subtitle)
                        .font(.system(size: 10))
                        .foregroundColor(.white.opacity(0.7))
                        .multilineTextAlignment(.center)
                }
            }
            .frame(maxWidth: .infinity)
            .padding(.vertical, 16)
            .background(
                RoundedRectangle(cornerRadius: 12)
                    .fill(.ultraThinMaterial)
                    .overlay(
                        RoundedRectangle(cornerRadius: 12)
                            .stroke(color.opacity(0.3), lineWidth: 1)
                    )
            )
        }
        .buttonStyle(PlainButtonStyle())
    }
}

// MARK: - Enhanced Task Section View
struct EnhancedTaskSectionView: View {
    let category: RingCategory
    let tasks: [DailyTask]
    let frequency: TaskFrequency
    let onTaskAction: (DailyTask, TaskAction) -> Void
    
    var completedCount: Int {
        tasks.filter { $0.status == .completed }.count
    }
    
    var progress: Double {
        tasks.isEmpty ? 0 : Double(completedCount) / Double(tasks.count)
    }
    
    var body: some View {
        VStack(spacing: 16) {
            // Section header with progress
            HStack {
                VStack(alignment: .leading, spacing: 4) {
                    Text(category.name)
                        .font(.title3)
                        .fontWeight(.bold)
                        .foregroundColor(.white)
                    
                    Text("(\(completedCount)/\(tasks.count))")
                        .font(.subheadline)
                        .foregroundColor(Color(category.color))
                }
                
                Spacer()
                
                // Progress circle
                ZStack {
                    Circle()
                        .stroke(Color(category.color).opacity(0.3), lineWidth: 4)
                        .frame(width: 40, height: 40)
                    
                    Circle()
                        .trim(from: 0, to: progress)
                        .stroke(Color(category.color), style: StrokeStyle(lineWidth: 4, lineCap: .round))
                        .frame(width: 40, height: 40)
                        .rotationEffect(.degrees(-90))
                    
                    Text("\(Int(progress * 100))%")
                        .font(.system(size: 10, weight: .bold))
                        .foregroundColor(.white)
                }
            }
            
            // Task list
            VStack(spacing: 12) {
                ForEach(tasks) { task in
                    EnhancedTaskCard(
                        task: task,
                        onAction: onTaskAction
                    )
                }
            }
        }
        .padding(.horizontal, 20)
        .padding(.vertical, 16)
        .background(
            RoundedRectangle(cornerRadius: 16)
                .fill(.ultraThinMaterial)
                .overlay(
                    RoundedRectangle(cornerRadius: 16)
                        .stroke(.white.opacity(0.1), lineWidth: 1)
                )
        )
    }
}

// MARK: - Enhanced Task Card
struct EnhancedTaskCard: View {
    let task: DailyTask
    let onAction: (DailyTask, TaskAction) -> Void
    
    var body: some View {
        VStack(spacing: 12) {
            // Main task row
            HStack(spacing: 16) {
                // Completion button
                completionButton
                
                // Task content
                taskContent
                
                Spacer()
                
                // Action button
                actionButton
            }
        }
        .padding(.horizontal, 16)
        .padding(.vertical, 12)
        .background(taskBackground)
    }
    
    private var completionButton: some View {
        Button(action: {
            onAction(task, .toggle)
        }) {
            Image(systemName: task.status == .completed ? "checkmark.circle.fill" : "circle")
                .font(.title2)
                .foregroundColor(task.status == .completed ? .green : .white.opacity(0.5))
        }
        .buttonStyle(PlainButtonStyle())
    }
    
    private var taskContent: some View {
        VStack(alignment: .leading, spacing: 4) {
            Text(task.title)
                .font(.system(size: 16, weight: .semibold))
                .foregroundColor(.white)
                .strikethrough(task.status == .completed)
            
            if !task.description.isEmpty {
                Text(task.description)
                    .font(.system(size: 13))
                    .foregroundColor(.white.opacity(0.7))
                    .lineLimit(2)
            }
        }
    }
    
    private var taskMetadata: some View {
        HStack(spacing: 8) {
            Spacer()
        }
    }
    
    private var actionButton: some View {
        Group {
            if task.title.lowercased().contains("linkedin") {
                linkButton(icon: "person.2.badge.plus", color: Color(red: 0.0, green: 0.47, blue: 0.84)) {
                    if let url = URL(string: "https://www.linkedin.com/messaging/") {
                        UIApplication.shared.open(url)
                    }
                }
            } else if task.title.lowercased().contains("apply") || task.title.lowercased().contains("job") {
                linkButton(icon: "briefcase.fill", color: Color(red: 0.9, green: 0.5, blue: 0.1)) {
                    if let url = URL(string: "https://www.indeed.com") {
                        UIApplication.shared.open(url)
                    }
                }
            } else {
                EmptyView()
            }
        }
    }
    
    private var taskBackground: some View {
        RoundedRectangle(cornerRadius: 12)
            .fill(task.status == .completed ? 
                  Color.green.opacity(0.1) : 
                  Color(.systemGray6).opacity(0.1))
            .overlay(
                RoundedRectangle(cornerRadius: 12)
                    .stroke(task.status == .completed ? 
                           Color.green.opacity(0.3) : 
                           Color.white.opacity(0.1), lineWidth: 1)
            )
    }
    
    private func linkButton(icon: String, color: Color, action: @escaping () -> Void) -> some View {
        Button(action: action) {
            Image(systemName: icon)
                .font(.system(size: 14))
                .foregroundColor(color)
                .padding(8)
                .background(
                    Circle()
                        .fill(color.opacity(0.2))
                        .overlay(
                            Circle()
                                .stroke(color.opacity(0.3), lineWidth: 1)
                        )
                )
        }
        .buttonStyle(PlainButtonStyle())
    }
}

// MARK: - Task Action Enum
enum TaskAction {
    case toggle
    case edit
    case delete
}

#Preview("Task Card - Pending") {
    let template = TaskTemplate(
        title: "Update LinkedIn Profile",
        description: "Optimize your headline, summary, and experience sections for better visibility",
        category: .hustle,
        estimatedTimeMinutes: 20,
        difficulty: .medium
    )
    let task = DailyTask(from: template, date: Date())
    
    return TaskCardView(
        task: task,
        onComplete: {},
        onSkip: {},
        onReset: {}
    )
    .padding()
}

#Preview("Task Card - Completed") {
    let template = TaskTemplate(
        title: "Complete Today's Exercise",
        description: "Finish your daily workout routine", 
        category: .grind,
        frequency: .daily,
        estimatedTimeMinutes: 30,
        difficulty: .easy
    )
    let task = DailyTask(from: template, date: Date(), status: .completed, completedAt: Date())
    
    TaskCardView(
        task: task,
        onComplete: {},
        onSkip: {},
        onReset: {}
    )
    .padding()
    .background(Color.black)
    .preferredColorScheme(.dark)
} 