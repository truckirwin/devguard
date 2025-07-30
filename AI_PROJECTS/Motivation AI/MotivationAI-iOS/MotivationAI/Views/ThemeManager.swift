import SwiftUI
import UIKit

// MARK: - Theme Manager
class ThemeManager: ObservableObject {
    @Published var isDarkMode: Bool = true
    
    static let shared = ThemeManager()
    
    private init() {}
}

// MARK: - Color Schemes
struct AppColors {
    
    // MARK: - Dark Theme Colors
    struct Dark {
        // Primary backgrounds
        static let primaryBackground = LinearGradient(
            colors: [
                Color(red: 0.05, green: 0.05, blue: 0.15),
                Color(red: 0.1, green: 0.1, blue: 0.2),
                Color(red: 0.15, green: 0.15, blue: 0.25)
            ],
            startPoint: .topLeading,
            endPoint: .bottomTrailing
        )
        
        static let secondaryBackground = Color(red: 0.12, green: 0.12, blue: 0.22)
        static let cardBackground = Color(red: 0.18, green: 0.18, blue: 0.28)
        static let surfaceBackground = Color(red: 0.15, green: 0.15, blue: 0.25)
        
        // Text colors
        static let primaryText = Color.white
        static let secondaryText = Color.white.opacity(0.8)
        static let tertiaryText = Color.white.opacity(0.6)
        
        // Accent colors (coordinated with rich theme)
        static let orange = Color(red: 1.0, green: 0.6, blue: 0.2)  // Rich orange
        static let blue = Color(red: 0.2, green: 0.6, blue: 1.0)    // Rich blue
        static let green = Color(red: 0.2, green: 0.8, blue: 0.4)   // Rich green
        static let purple = Color(red: 0.7, green: 0.3, blue: 0.9)  // Rich purple
        static let red = Color(red: 1.0, green: 0.3, blue: 0.3)     // Rich red
        static let yellow = Color(red: 1.0, green: 0.8, blue: 0.2)  // Rich yellow
        static let cyan = Color(red: 0.2, green: 0.8, blue: 0.9)    // Rich cyan
        static let indigo = Color(red: 0.4, green: 0.3, blue: 0.9)  // Rich indigo
        
        // Utility colors
        static let success = green
        static let warning = orange
        static let error = red
        static let info = blue
    }
    
    // MARK: - Light Theme Colors (for future coordination)
    struct Light {
        static let primaryBackground = LinearGradient(
            colors: [Color.white, Color(red: 0.98, green: 0.98, blue: 1.0)],
            startPoint: .topLeading,
            endPoint: .bottomTrailing
        )
        
        static let secondaryBackground = Color(red: 0.95, green: 0.95, blue: 0.97)
        static let cardBackground = Color.white
        static let surfaceBackground = Color(red: 0.98, green: 0.98, blue: 1.0)
        
        static let primaryText = Color.primary
        static let secondaryText = Color.secondary
        static let tertiaryText = Color.secondary.opacity(0.7)
        
        // Matching accent colors but lighter
        static let orange = Color.orange
        static let blue = Color.blue
        static let green = Color.green
        static let purple = Color.purple
        static let red = Color.red
        static let yellow = Color.yellow
        static let cyan = Color.cyan
        static let indigo = Color.indigo
        
        static let success = Color.green
        static let warning = Color.orange
        static let error = Color.red
        static let info = Color.blue
    }
    
    // MARK: - Current Theme Accessor
    static var current: AppColors.Dark.Type {
        return AppColors.Dark.self  // Always dark for now
    }
}

// MARK: - Card Styles
struct AppCardStyle: ViewModifier {
    let isDarkMode: Bool = true
    
    func body(content: Content) -> some View {
        content
            .background(
                RoundedRectangle(cornerRadius: 16)
                    .fill(isDarkMode ? AppColors.Dark.cardBackground : AppColors.Light.cardBackground)
                    .overlay(
                        RoundedRectangle(cornerRadius: 16)
                            .stroke(
                                isDarkMode ? 
                                Color.white.opacity(0.1) : 
                                Color.black.opacity(0.1), 
                                lineWidth: 1
                            )
                    )
            )
            .shadow(
                color: isDarkMode ? Color.black.opacity(0.3) : Color.black.opacity(0.1),
                radius: isDarkMode ? 8 : 4,
                x: 0,
                y: isDarkMode ? 4 : 2
            )
    }
}

// MARK: - Gradient Button Style
struct GradientButtonStyle: ButtonStyle {
    let color: Color
    let isLarge: Bool
    
    init(color: Color, isLarge: Bool = false) {
        self.color = color
        self.isLarge = isLarge
    }
    
    func makeBody(configuration: Configuration) -> some View {
        configuration.label
            .foregroundColor(.white)
            .fontWeight(.semibold)
            .frame(height: isLarge ? 56 : 44)
            .frame(maxWidth: .infinity)
            .background(
                LinearGradient(
                    colors: [
                        color,
                        color.opacity(0.8)
                    ],
                    startPoint: .topLeading,
                    endPoint: .bottomTrailing
                )
            )
            .cornerRadius(12)
            .scaleEffect(configuration.isPressed ? 0.98 : 1.0)
            .opacity(configuration.isPressed ? 0.9 : 1.0)
            .animation(.easeInOut(duration: 0.1), value: configuration.isPressed)
    }
}

// MARK: - Extensions
extension View {
    func appCardStyle() -> some View {
        modifier(AppCardStyle())
    }
    
    func gradientButton(color: Color, isLarge: Bool = false) -> some View {
        buttonStyle(GradientButtonStyle(color: color, isLarge: isLarge))
    }
} 