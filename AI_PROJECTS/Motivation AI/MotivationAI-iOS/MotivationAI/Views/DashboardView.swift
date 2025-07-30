import SwiftUI

struct DashboardView: View {
    @EnvironmentObject var appViewModel: AppViewModel
    
    private func openLinkedInJobs() {
        if let url = URL(string: "https://www.linkedin.com/jobs/") {
            UIApplication.shared.open(url)
        }
    }
    
    private func openLinkedInMessages() {
        if let url = URL(string: "https://www.linkedin.com/messaging/") {
            UIApplication.shared.open(url)
        }
    }
    
    var body: some View {
        NavigationView {
            ScrollView {
                VStack(spacing: 24) {
                    // App Title with Profile
                    HStack {
                        Text("Rise and Grind!")
                            .font(.largeTitle)
                            .fontWeight(.bold)
                        Spacer()
                        Circle()
                            .fill(Color.blue)
                            .frame(width: 35, height: 35)
                            .overlay(
                                Text("J")
                                    .font(.title3)
                                    .fontWeight(.bold)
                                    .foregroundColor(.white)
                            )
                    }
                    .padding(.horizontal)
                    
                    // Progress Rings
                    HStack(spacing: 20) {
                        ProgressRing(
                            value: 0,
                            label: "Tasks",
                            color: .blue
                        )
                        
                        ProgressRing(
                            value: 7,
                            label: "Day Streak",
                            color: .orange
                        )
                        
                        ProgressRing(
                            value: "L3",
                            label: "Level",
                            color: .green
                        )
                    }
                    .padding(.horizontal)
                    
                    // Quick Actions
                    HStack(spacing: 12) {
                        QuickActionCard(
                            icon: "envelope.fill",
                            label: "Applications",
                            color: .green
                        ) {
                            openLinkedInJobs()
                        }
                        
                        QuickActionCard(
                            icon: "message.fill",
                            label: "Interviews",
                            color: .orange
                        ) {
                            openLinkedInMessages()
                        }
                        
                        QuickActionCard(
                            icon: "brain.head.profile",
                            label: "Skills",
                            color: .purple
                        ) {
                            // Navigate to Learning tab
                        }
                    }
                    .padding(.horizontal)
                    
                    // Activity Graph
                    ActivityOverviewCard()
                        .padding(.horizontal)
                    
                    // Let's Go! Action Buttons
                    VStack(alignment: .leading, spacing: 12) {
                        HStack {
                            Image(systemName: "bolt.fill")
                                .foregroundColor(.blue)
                            Text("Let's Go!")
                                .font(.headline)
                                .fontWeight(.bold)
                        }
                        
                        VStack(spacing: 8) {
                            HStack(spacing: 12) {
                                LetsGoButton(
                                    icon: "sunrise.fill",
                                    label: "Morning Power",
                                    subtitle: "Rise & dominate",
                                    color: .orange
                                ) {
                                    let morningMessages = DemoVideoScripts.getMorningDemos()
                                    if let message = morningMessages.randomElement() {
                                        appViewModel.showAnimatedTextMessage(message)
                                    }
                                }
                                
                                LetsGoButton(
                                    icon: "bolt.circle.fill",
                                    label: "Midday Push",
                                    subtitle: "Keep momentum",
                                    color: .blue
                                ) {
                                    let middayMessages = DemoVideoScripts.getMiddayDemos()
                                    if let message = middayMessages.randomElement() {
                                        appViewModel.showAnimatedTextMessage(message)
                                    }
                                }
                            }
                            
                            HStack(spacing: 12) {
                                LetsGoButton(
                                    icon: "flame.fill",
                                    label: "Afternoon Fire",
                                    subtitle: "Final stretch",
                                    color: .red
                                ) {
                                    let afternoonMessages = DemoVideoScripts.getAfternoonDemos()
                                    if let message = afternoonMessages.randomElement() {
                                        appViewModel.showAnimatedTextMessage(message)
                                    }
                                }
                                
                                LetsGoButton(
                                    icon: "star.fill",
                                    label: "Victory Lap",
                                    subtitle: "Celebrate wins",
                                    color: .purple
                                ) {
                                    let eveningMessages = DemoVideoScripts.getEveningDemos()
                                    if let message = eveningMessages.randomElement() {
                                        appViewModel.showAnimatedTextMessage(message)
                                    }
                                }
                            }
                        }
                    }
                    .padding(.horizontal)
                    
                    Spacer(minLength: 80)
                }
            }
            .navigationBarTitleDisplayMode(.inline)
        }
    }
}

// MARK: - Supporting Views

struct ProgressRing: View {
    let value: Any
    let label: String
    let color: Color
    
    var body: some View {
        VStack(spacing: 8) {
            ZStack {
                Circle()
                    .stroke(color.opacity(0.2), lineWidth: 8)
                    .frame(width: 60, height: 60)
                
                Circle()
                    .trim(from: 0, to: 0.7)
                    .stroke(color, style: StrokeStyle(lineWidth: 8, lineCap: .round))
                    .frame(width: 60, height: 60)
                    .rotationEffect(.degrees(-90))
                
                Text("\(value)")
                    .font(.title2)
                    .fontWeight(.bold)
                    .foregroundColor(.primary)
            }
            
            Text(label)
                .font(.caption)
                .foregroundColor(.secondary)
        }
    }
}

struct QuickActionCard: View {
    let icon: String
    let label: String
    let color: Color
    let action: () -> Void
    
    var body: some View {
        Button(action: action) {
            VStack(spacing: 4) {
                Image(systemName: icon)
                    .font(.title3)
                    .foregroundColor(color)
                
                Text(label)
                    .font(.caption2)
                    .foregroundColor(.primary)
                    .fontWeight(.medium)
            }
            .frame(maxWidth: .infinity)
            .frame(height: 50)
            .background(color.opacity(0.1))
            .cornerRadius(8)
        }
        .buttonStyle(PlainButtonStyle())
    }
}

struct LetsGoButton: View {
    let icon: String
    let label: String
    let subtitle: String
    let color: Color
    let action: () -> Void
    
    var body: some View {
        Button(action: action) {
            VStack(spacing: 6) {
                Image(systemName: icon)
                    .font(.title2)
                    .foregroundColor(color)
                
                Text(label)
                    .font(.caption)
                    .fontWeight(.semibold)
                    .foregroundColor(.primary)
                
                Text(subtitle)
                    .font(.caption2)
                    .foregroundColor(.secondary)
                    .multilineTextAlignment(.center)
            }
            .frame(maxWidth: .infinity)
            .frame(height: 80)
            .background(color.opacity(0.1))
            .cornerRadius(12)
            .overlay(
                RoundedRectangle(cornerRadius: 12)
                    .stroke(color.opacity(0.3), lineWidth: 1)
            )
        }
        .buttonStyle(PlainButtonStyle())
    }
}

struct ActivityOverviewCard: View {
    @State private var activityData: [ActivityDataPoint] = []
    @State private var selectedTimeFrame = 3 // Default to 6 weeks (index 3)
    
    private let timeFrames = ["1 Day", "1 Week", "3 Weeks", "6 Weeks"]
    private let timeFrameDays = [24, 7, 21, 42] // 24 hours, 7 days, 21 days, 42 days
    
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            VStack(spacing: 12) {
                HStack {
                    Image(systemName: "chart.xyaxis.line")
                        .foregroundColor(.cyan)
                    Text("Activity Metrics")
                        .font(.headline)
                        .fontWeight(.bold)
                    Spacer()
                    Text("\(timeFrames[selectedTimeFrame]) Analysis")
                        .font(.caption)
                        .foregroundColor(.secondary)
                        .padding(.horizontal, 8)
                        .padding(.vertical, 2)
                        .background(Color.cyan.opacity(0.1))
                        .cornerRadius(4)
                }
                
                // Time Frame Selector
                Picker("Time Frame", selection: $selectedTimeFrame) {
                    ForEach(0..<timeFrames.count, id: \.self) { index in
                        Text(timeFrames[index])
                            .tag(index)
                    }
                }
                .pickerStyle(SegmentedPickerStyle())
                .onChange(of: selectedTimeFrame) { _ in
                    generateSampleData()
                }
            }
            
            // Technical Chart
            VStack(spacing: 8) {
                TechnicalChartView(activityData: activityData)
                    .frame(height: 180)
                
                // Technical Legend
                HStack(spacing: 20) {
                    TechnicalLegendItem(color: .purple, label: "COMMS")
                    TechnicalLegendItem(color: .green, label: "TASKS")
                    TechnicalLegendItem(color: .orange, label: "SKILLS")
                    TechnicalLegendItem(color: .cyan, label: "HEALTH")
                }
                .padding(.top, 8)
            }
        }
        .padding()
        .background(Color(.systemBackground))
        .cornerRadius(12)
        .shadow(color: .black.opacity(0.1), radius: 4, x: 0, y: 2)
        .onAppear {
            generateSampleData()
        }
    }
    
    private func getValue(for dataPoint: ActivityDataPoint, category: String) -> Double {
        switch category {
        case "health": return dataPoint.health
        case "tasks": return dataPoint.tasks
        case "skills": return dataPoint.skills
        case "communications": return dataPoint.communications
        default: return 0
        }
    }
    
    private func generateSampleData() {
        let calendar = Calendar.current
        let today = Date()
        let dayCount = timeFrameDays[selectedTimeFrame]
        
        activityData = (0..<dayCount).compactMap { dayOffset in
            guard let date = calendar.date(byAdding: .day, value: -dayOffset, to: today) else { return nil }
            
            let dayOfWeek = calendar.component(.weekday, from: date)
            
            // Simulate realistic patterns - lower activity on weekends, trends over time
            let weekendMultiplier = (dayOfWeek == 1 || dayOfWeek == 7) ? 0.6 : 1.0
            let trendMultiplier = 1.0 + (Double(dayCount - dayOffset) / Double(dayCount * 5)) // Slight upward trend
            
            // Generate different label formats based on time frame
            let dayLabel: String
            switch selectedTimeFrame {
            case 0: // 1 Day
                let formatter = DateFormatter()
                formatter.dateFormat = "HH:mm"
                // For 1 day, show hourly intervals (24 hours)
                let hourOffset = dayOffset
                dayLabel = formatter.string(from: calendar.date(byAdding: .hour, value: -hourOffset, to: today) ?? date)
            case 1: // 1 Week
                let formatter = DateFormatter()
                formatter.dateFormat = "EEE"
                dayLabel = formatter.string(from: date)
            case 2: // 3 Weeks
                dayLabel = "D\(dayCount - dayOffset)"
            default: // 6 Weeks
                dayLabel = "W\(((dayCount - dayOffset - 1) / 7) + 1)"
            }
            
            return ActivityDataPoint(
                day: dayLabel,
                health: Double.random(in: 40...95) * weekendMultiplier * trendMultiplier,
                tasks: Double.random(in: 25...85) * weekendMultiplier * trendMultiplier,
                skills: Double.random(in: 15...70) * weekendMultiplier * trendMultiplier,
                communications: Double.random(in: 10...50) * weekendMultiplier * trendMultiplier
            )
        }.reversed()
    }
}

struct LegendItem: View {
    let color: Color
    let label: String
    
    var body: some View {
        HStack(spacing: 4) {
            Circle()
                .fill(color)
                .frame(width: 8, height: 8)
            Text(label)
                .font(.caption2)
                .foregroundColor(.secondary)
        }
    }
}

struct TechnicalChartView: View {
    let activityData: [ActivityDataPoint]
    
    var body: some View {
        GeometryReader { geometry in
            let maxValue = activityData.map { max($0.health, $0.tasks, $0.skills, $0.communications) }.max() ?? 100
            let chartWidth = geometry.size.width
            let chartHeight = geometry.size.height - 40
            let stepWidth = chartWidth / CGFloat(max(activityData.count - 1, 1))
            
            ZStack {
                TechnicalGridView(chartWidth: chartWidth, chartHeight: chartHeight, maxValue: maxValue, dataCount: activityData.count)
                
                TechnicalDataAreasView(
                    activityData: activityData,
                    chartWidth: chartWidth,
                    chartHeight: chartHeight,
                    maxValue: maxValue,
                    stepWidth: stepWidth
                )
                
                TechnicalAxisLabelsView(chartWidth: chartWidth, chartHeight: chartHeight, activityData: activityData)
            }
        }
    }
}

struct TechnicalGridView: View {
    let chartWidth: CGFloat
    let chartHeight: CGFloat
    let maxValue: Double
    let dataCount: Int
    
    var body: some View {
        ZStack {
            // Technical grid background
            Path { path in
                for i in 0...8 {
                    let y = chartHeight * CGFloat(i) / 8
                    path.move(to: CGPoint(x: 0, y: y))
                    path.addLine(to: CGPoint(x: chartWidth, y: y))
                }
                let verticalLines = min(dataCount, 8)
                for i in 0...verticalLines {
                    let x = chartWidth * CGFloat(i) / CGFloat(verticalLines)
                    path.move(to: CGPoint(x: x, y: 0))
                    path.addLine(to: CGPoint(x: x, y: chartHeight))
                }
            }
            .stroke(Color.gray.opacity(0.15), lineWidth: 0.5)
            
            // Major grid lines
            Path { path in
                for i in 0...4 {
                    let y = chartHeight * CGFloat(i) / 4
                    path.move(to: CGPoint(x: 0, y: y))
                    path.addLine(to: CGPoint(x: chartWidth, y: y))
                }
            }
            .stroke(Color.gray.opacity(0.3), lineWidth: 1)
            
            // Y-axis values
            VStack {
                ForEach(0..<5) { i in
                    HStack {
                        Text("\(Int(maxValue * Double(4-i) / 4))")
                            .font(.system(size: 10, design: .monospaced))
                            .foregroundColor(.secondary)
                        Spacer()
                    }
                    if i < 4 { Spacer() }
                }
            }
            .frame(width: 30, height: chartHeight)
            .position(x: -15, y: chartHeight/2)
        }
    }
}

struct TechnicalDataAreasView: View {
    let activityData: [ActivityDataPoint]
    let chartWidth: CGFloat
    let chartHeight: CGFloat
    let maxValue: Double
    let stepWidth: CGFloat
    
    var body: some View {
        ZStack {
            // Layer each area chart with transparency
            TechnicalAreaView(
                activityData: activityData,
                category: "health",
                color: Color.cyan,
                chartHeight: chartHeight,
                maxValue: maxValue,
                stepWidth: stepWidth,
                baselineOffset: 0
            )
            
            TechnicalAreaView(
                activityData: activityData,
                category: "skills",
                color: Color.orange,
                chartHeight: chartHeight,
                maxValue: maxValue,
                stepWidth: stepWidth,
                baselineOffset: 0
            )
            
            TechnicalAreaView(
                activityData: activityData,
                category: "tasks",
                color: Color.green,
                chartHeight: chartHeight,
                maxValue: maxValue,
                stepWidth: stepWidth,
                baselineOffset: 0
            )
            
            TechnicalAreaView(
                activityData: activityData,
                category: "communications",
                color: Color.purple,
                chartHeight: chartHeight,
                maxValue: maxValue,
                stepWidth: stepWidth,
                baselineOffset: 0
            )
        }
    }
}

struct TechnicalAreaView: View {
    let activityData: [ActivityDataPoint]
    let category: String
    let color: Color
    let chartHeight: CGFloat
    let maxValue: Double
    let stepWidth: CGFloat
    let baselineOffset: CGFloat
    
    var body: some View {
        // Filled area chart
        Path { path in
            guard !activityData.isEmpty else { return }
            
            // Start from bottom left
            let firstValue = getValue(for: activityData[0], category: category)
            let firstY = chartHeight - (chartHeight * CGFloat(firstValue) / CGFloat(maxValue)) + baselineOffset
            path.move(to: CGPoint(x: 0, y: chartHeight))
            path.addLine(to: CGPoint(x: 0, y: firstY))
            
            // Draw the top curve
            for (i, dataPoint) in activityData.enumerated() {
                let value = getValue(for: dataPoint, category: category)
                let x = CGFloat(i) * stepWidth
                let y = chartHeight - (chartHeight * CGFloat(value) / CGFloat(maxValue)) + baselineOffset
                path.addLine(to: CGPoint(x: x, y: y))
            }
            
            // Close the area by going to bottom right and back to start
            let lastX = CGFloat(activityData.count - 1) * stepWidth
            path.addLine(to: CGPoint(x: lastX, y: chartHeight))
            path.addLine(to: CGPoint(x: 0, y: chartHeight))
        }
        .fill(LinearGradient(
            gradient: Gradient(colors: [
                color.opacity(0.4),
                color.opacity(0.1)
            ]),
            startPoint: .top,
            endPoint: .bottom
        ))
        
        // Add a subtle stroke on top
        Path { path in
            for (i, dataPoint) in activityData.enumerated() {
                let value = getValue(for: dataPoint, category: category)
                let x = CGFloat(i) * stepWidth
                let y = chartHeight - (chartHeight * CGFloat(value) / CGFloat(maxValue)) + baselineOffset
                
                if i == 0 {
                    path.move(to: CGPoint(x: x, y: y))
                } else {
                    path.addLine(to: CGPoint(x: x, y: y))
                }
            }
        }
        .stroke(color.opacity(0.7), style: StrokeStyle(lineWidth: 1.5, lineCap: .round, lineJoin: .round))
    }
    
    private func getValue(for dataPoint: ActivityDataPoint, category: String) -> Double {
        switch category {
        case "health": return dataPoint.health
        case "tasks": return dataPoint.tasks
        case "skills": return dataPoint.skills
        case "communications": return dataPoint.communications
        default: return 0
        }
    }
}

struct TechnicalAxisLabelsView: View {
    let chartWidth: CGFloat
    let chartHeight: CGFloat
    let activityData: [ActivityDataPoint]
    
    var body: some View {
        HStack {
            // Show every nth label to avoid overcrowding
            let labelInterval = max(1, activityData.count / 6)
            ForEach(Array(activityData.enumerated().filter { $0.offset % labelInterval == 0 }), id: \.offset) { index, dataPoint in
                Text(dataPoint.day)
                    .font(.system(size: 10, design: .monospaced))
                    .foregroundColor(.secondary)
                if index < activityData.count - labelInterval { Spacer() }
            }
        }
        .position(x: chartWidth/2, y: chartHeight + 20)
    }
}

struct TechnicalLegendItem: View {
    let color: Color
    let label: String
    
    var body: some View {
        HStack(spacing: 6) {
            ZStack {
                Circle()
                    .fill(Color.black)
                    .frame(width: 10, height: 10)
                Circle()
                    .fill(color)
                    .frame(width: 8, height: 8)
                Rectangle()
                    .fill(color)
                    .frame(width: 12, height: 2)
            }
            Text(label)
                .font(.system(size: 12, design: .monospaced))
                .fontWeight(.semibold)
                .foregroundColor(.primary)
        }
    }
}

struct ActivityDataPoint: Identifiable {
    let id = UUID()
    let day: String
    let health: Double
    let tasks: Double
    let skills: Double
    let communications: Double
}

#Preview {
    DashboardView()
        .environmentObject(AppViewModel())
} 