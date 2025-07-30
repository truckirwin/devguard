import SwiftUI

struct ContentView: View {
    var body: some View {
        ZStack {
            // Pure black background to match design
            Color.black.ignoresSafeArea()
            
            VStack(spacing: 0) {
                // App Header
                VStack(spacing: 12) {
                    Image(systemName: "brain.head.profile")
                        .font(.system(size: 60, weight: .light))
                        .foregroundColor(.orange)
                    
                    Text("Motivation AI")
                        .font(.largeTitle)
                        .fontWeight(.bold)
                        .foregroundColor(.white)
                    
                    Text("Agentic AI for Personalized Motivation")
                        .font(.headline)
                        .foregroundColor(.gray)
                        .multilineTextAlignment(.center)
                }
                .padding(.top, 40)
                .padding(.bottom, 20)
                
                // AI Message Generator (Full Screen)
                AIMessageGeneratorView()
            }
        }
        .preferredColorScheme(.dark)
    }
}

struct ContentView_Previews: PreviewProvider {
    static var previews: some View {
        ContentView()
    }
} 