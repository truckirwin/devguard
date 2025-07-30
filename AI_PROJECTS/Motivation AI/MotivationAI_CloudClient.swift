import Foundation
import SwiftUI
import Combine

// MARK: - Data Models

struct User: Codable {
    let id: String
    let email: String
    let subscriptionTier: String
    let usageCount: Int
    
    enum CodingKeys: String, CodingKey {
        case id, email
        case subscriptionTier = "subscription_tier"
        case usageCount = "usage_count"
    }
}

struct AuthResponse: Codable {
    let success: Bool
    let token: String?
    let user: User?
    let error: String?
}

struct GenerationRequest: Codable {
    let userInput: String
    let intensity: Int
    let languageClean: Int
    let humorStyle: Int
    let actionOrientation: Int
    let messageLength: Int
    let musicStyle: Int
    let visualStyle: Int
    
    enum CodingKeys: String, CodingKey {
        case userInput = "user_input"
        case intensity
        case languageClean = "language_clean"
        case humorStyle = "humor_style"
        case actionOrientation = "action_orientation"
        case messageLength = "message_length"
        case musicStyle = "music_style"
        case visualStyle = "visual_style"
    }
}

struct GenerationResponse: Codable {
    let success: Bool
    let requestId: String?
    let messageText: String?
    let audioUrl: String?
    let imageUrl: String?
    let videoUrl: String?
    let captions: CaptionsData?
    let metadata: GenerationMetadata?
    let error: String?
    let upgradeRequired: Bool?
    
    enum CodingKeys: String, CodingKey {
        case success
        case requestId = "request_id"
        case messageText = "message_text"
        case audioUrl = "audio_url"
        case imageUrl = "image_url"
        case videoUrl = "video_url"
        case captions, metadata, error
        case upgradeRequired = "upgrade_required"
    }
}

struct CaptionsData: Codable {
    let version: String
    let language: String
    let segments: [CaptionSegment]
}

struct CaptionSegment: Codable {
    let id: Int
    let start: Double
    let end: Double
    let text: String
}

struct GenerationMetadata: Codable {
    let generatedAt: String
    let generationTime: Double
    let contentType: String
    
    enum CodingKeys: String, CodingKey {
        case generatedAt = "generated_at"
        case generationTime = "generation_time"
        case contentType = "content_type"
    }
}

struct SubscriptionInfo: Codable {
    let subscriptionTier: String
    let subscriptionStatus: String
    let usageCount: Int
    let limits: SubscriptionLimits
    let usagePercentage: Double
    
    enum CodingKeys: String, CodingKey {
        case subscriptionTier = "subscription_tier"
        case subscriptionStatus = "subscription_status"
        case usageCount = "usage_count"
        case limits
        case usagePercentage = "usage_percentage"
    }
}

struct SubscriptionLimits: Codable {
    let generationsPerMonth: Int
    let maxLengthSeconds: Int
    let videoQuality: String
    let premiumVoices: Bool
    let customMusic: Bool
    let bulkGeneration: Bool?
    let apiAccess: Bool?
    
    enum CodingKeys: String, CodingKey {
        case generationsPerMonth = "generations_per_month"
        case maxLengthSeconds = "max_length_seconds"
        case videoQuality = "video_quality"
        case premiumVoices = "premium_voices"
        case customMusic = "custom_music"
        case bulkGeneration = "bulk_generation"
        case apiAccess = "api_access"
    }
}

// MARK: - Cloud Service

class MotivationAICloudService: ObservableObject {
    static let shared = MotivationAICloudService()
    
    @Published var currentUser: User?
    @Published var subscriptionInfo: SubscriptionInfo?
    @Published var isLoading = false
    @Published var error: String?
    
    private let baseURL: String
    private let session = URLSession.shared
    private var authToken: String? {
        get { UserDefaults.standard.string(forKey: "auth_token") }
        set { 
            if let token = newValue {
                UserDefaults.standard.set(token, forKey: "auth_token")
            } else {
                UserDefaults.standard.removeObject(forKey: "auth_token")
            }
        }
    }
    
    private init() {
        // Configure for your production server
        #if DEBUG
        self.baseURL = "http://localhost:8080"  // Local development
        #else
        self.baseURL = "https://your-production-server.com"  // Production
        #endif
        
        // Load stored user data
        loadStoredUser()
    }
    
    private func loadStoredUser() {
        if let token = authToken,
           let userData = UserDefaults.standard.data(forKey: "current_user"),
           let user = try? JSONDecoder().decode(User.self, from: userData) {
            self.currentUser = user
            Task {
                await loadSubscriptionInfo()
            }
        }
    }
    
    private func saveUser(_ user: User) {
        self.currentUser = user
        if let userData = try? JSONEncoder().encode(user) {
            UserDefaults.standard.set(userData, forKey: "current_user")
        }
    }
    
    // MARK: - Authentication
    
    func register(email: String, password: String) async -> Bool {
        await withCheckedContinuation { continuation in
            let request = createRequest(endpoint: "/api/auth/register", method: "POST")
            let body = ["email": email, "password": password]
            
            performRequest(request, body: body, responseType: AuthResponse.self) { result in
                DispatchQueue.main.async {
                    switch result {
                    case .success(let response):
                        if response.success, let token = response.token, let user = response.user {
                            self.authToken = token
                            self.saveUser(user)
                            self.error = nil
                            continuation.resume(returning: true)
                        } else {
                            self.error = response.error ?? "Registration failed"
                            continuation.resume(returning: false)
                        }
                    case .failure(let error):
                        self.error = error.localizedDescription
                        continuation.resume(returning: false)
                    }
                }
            }
        }
    }
    
    func login(email: String, password: String) async -> Bool {
        await withCheckedContinuation { continuation in
            let request = createRequest(endpoint: "/api/auth/login", method: "POST")
            let body = ["email": email, "password": password]
            
            performRequest(request, body: body, responseType: AuthResponse.self) { result in
                DispatchQueue.main.async {
                    switch result {
                    case .success(let response):
                        if response.success, let token = response.token, let user = response.user {
                            self.authToken = token
                            self.saveUser(user)
                            self.error = nil
                            Task {
                                await self.loadSubscriptionInfo()
                            }
                            continuation.resume(returning: true)
                        } else {
                            self.error = response.error ?? "Login failed"
                            continuation.resume(returning: false)
                        }
                    case .failure(let error):
                        self.error = error.localizedDescription
                        continuation.resume(returning: false)
                    }
                }
            }
        }
    }
    
    func logout() {
        authToken = nil
        currentUser = nil
        subscriptionInfo = nil
        UserDefaults.standard.removeObject(forKey: "current_user")
        error = nil
    }
    
    // MARK: - Content Generation
    
    func generateContent(request: GenerationRequest) async -> GenerationResponse? {
        await withCheckedContinuation { continuation in
            isLoading = true
            
            let apiRequest = createAuthenticatedRequest(endpoint: "/api/generate", method: "POST")
            
            performRequest(apiRequest, body: request, responseType: GenerationResponse.self) { result in
                DispatchQueue.main.async {
                    self.isLoading = false
                    
                    switch result {
                    case .success(let response):
                        if !response.success {
                            self.error = response.error
                        }
                        continuation.resume(returning: response)
                    case .failure(let error):
                        self.error = error.localizedDescription
                        continuation.resume(returning: nil)
                    }
                }
            }
        }
    }
    
    // MARK: - Subscription Management
    
    func loadSubscriptionInfo() async {
        let request = createAuthenticatedRequest(endpoint: "/api/user/subscription", method: "GET")
        
        let result = await performRequestAsync(request, responseType: SubscriptionInfo.self)
        
        DispatchQueue.main.async {
            switch result {
            case .success(let info):
                self.subscriptionInfo = info
            case .failure(let error):
                self.error = error.localizedDescription
            }
        }
    }
    
    func upgradeSubscription(to tier: String) async -> Bool {
        await withCheckedContinuation { continuation in
            let request = createAuthenticatedRequest(endpoint: "/api/subscription/upgrade", method: "POST")
            let body = ["tier": tier]
            
            performRequest(request, body: body, responseType: [String: Any].self) { result in
                DispatchQueue.main.async {
                    switch result {
                    case .success(let response):
                        if let success = response["success"] as? Bool, success {
                            Task {
                                await self.loadSubscriptionInfo()
                            }
                            continuation.resume(returning: true)
                        } else {
                            self.error = response["error"] as? String ?? "Upgrade failed"
                            continuation.resume(returning: false)
                        }
                    case .failure(let error):
                        self.error = error.localizedDescription
                        continuation.resume(returning: false)
                    }
                }
            }
        }
    }
    
    // MARK: - Helper Methods
    
    private func createRequest(endpoint: String, method: String) -> URLRequest {
        let url = URL(string: baseURL + endpoint)!
        var request = URLRequest(url: url)
        request.httpMethod = method
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        return request
    }
    
    private func createAuthenticatedRequest(endpoint: String, method: String) -> URLRequest {
        var request = createRequest(endpoint: endpoint, method: method)
        if let token = authToken {
            request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        }
        return request
    }
    
    private func performRequest<T: Codable, B: Codable>(
        _ request: URLRequest,
        body: B? = nil,
        responseType: T.Type,
        completion: @escaping (Result<T, Error>) -> Void
    ) {
        var finalRequest = request
        
        if let body = body {
            do {
                finalRequest.httpBody = try JSONEncoder().encode(body)
            } catch {
                completion(.failure(error))
                return
            }
        }
        
        session.dataTask(with: finalRequest) { data, response, error in
            if let error = error {
                completion(.failure(error))
                return
            }
            
            guard let data = data else {
                completion(.failure(URLError(.badServerResponse)))
                return
            }
            
            do {
                let result = try JSONDecoder().decode(T.self, from: data)
                completion(.success(result))
            } catch {
                completion(.failure(error))
            }
        }.resume()
    }
    
    private func performRequestAsync<T: Codable>(
        _ request: URLRequest,
        responseType: T.Type
    ) async -> Result<T, Error> {
        do {
            let (data, _) = try await session.data(for: request)
            let result = try JSONDecoder().decode(T.self, from: data)
            return .success(result)
        } catch {
            return .failure(error)
        }
    }
}

// MARK: - SwiftUI Views

struct MotivationAICloudApp: View {
    @StateObject private var cloudService = MotivationAICloudService.shared
    
    var body: some View {
        NavigationView {
            if cloudService.currentUser == nil {
                AuthenticationView()
            } else {
                MainAppView()
            }
        }
        .environmentObject(cloudService)
    }
}

struct AuthenticationView: View {
    @EnvironmentObject var cloudService: MotivationAICloudService
    @State private var email = ""
    @State private var password = ""
    @State private var isLogin = true
    @State private var isLoading = false
    
    var body: some View {
        VStack(spacing: 30) {
            // Header
            VStack(spacing: 12) {
                Image(systemName: "brain.head.profile")
                    .font(.system(size: 60, weight: .light))
                    .foregroundColor(.orange)
                
                Text("Motivation AI")
                    .font(.largeTitle)
                    .fontWeight(.bold)
                
                Text("AI-Powered Personal Motivation")
                    .font(.headline)
                    .foregroundColor(.secondary)
            }
            .padding(.top, 40)
            
            // Auth Form
            VStack(spacing: 20) {
                TextField("Email", text: $email)
                    .textFieldStyle(RoundedBorderTextFieldStyle())
                    .autocapitalization(.none)
                    .keyboardType(.emailAddress)
                
                SecureField("Password", text: $password)
                    .textFieldStyle(RoundedBorderTextFieldStyle())
                
                if let error = cloudService.error {
                    Text(error)
                        .foregroundColor(.red)
                        .font(.caption)
                }
                
                Button(action: authenticate) {
                    if isLoading {
                        ProgressView()
                            .progressViewStyle(CircularProgressViewStyle(tint: .white))
                    } else {
                        Text(isLogin ? "Login" : "Sign Up")
                    }
                }
                .frame(maxWidth: .infinity)
                .padding()
                .background(Color.orange)
                .foregroundColor(.white)
                .cornerRadius(10)
                .disabled(isLoading || email.isEmpty || password.isEmpty)
                
                Button(action: { isLogin.toggle() }) {
                    Text(isLogin ? "Need an account? Sign up" : "Have an account? Login")
                        .foregroundColor(.orange)
                }
            }
            .padding(.horizontal, 40)
            
            Spacer()
        }
        .background(Color.black.ignoresSafeArea())
        .preferredColorScheme(.dark)
    }
    
    private func authenticate() {
        isLoading = true
        
        Task {
            let success: Bool
            if isLogin {
                success = await cloudService.login(email: email, password: password)
            } else {
                success = await cloudService.register(email: email, password: password)
            }
            
            DispatchQueue.main.async {
                isLoading = false
                if success {
                    email = ""
                    password = ""
                }
            }
        }
    }
}

struct MainAppView: View {
    @EnvironmentObject var cloudService: MotivationAICloudService
    
    var body: some View {
        TabView {
            GeneratorView()
                .tabItem {
                    Image(systemName: "brain.head.profile")
                    Text("Generate")
                }
            
            SubscriptionView()
                .tabItem {
                    Image(systemName: "crown")
                    Text("Subscription")
                }
            
            ProfileView()
                .tabItem {
                    Image(systemName: "person")
                    Text("Profile")
                }
        }
        .preferredColorScheme(.dark)
    }
}

struct GeneratorView: View {
    @EnvironmentObject var cloudService: MotivationAICloudService
    @State private var userInput = ""
    @State private var intensity = 50.0
    @State private var languageClean = 50.0
    @State private var humorStyle = 50.0
    @State private var actionOrientation = 50.0
    @State private var messageLength = 50.0
    @State private var musicStyle = 50.0
    @State private var visualStyle = 50.0
    @State private var generationResult: GenerationResponse?
    
    var body: some View {
        ScrollView {
            VStack(spacing: 25) {
                // Header
                VStack(spacing: 12) {
                    Text("Create Your Motivation")
                        .font(.largeTitle)
                        .fontWeight(.bold)
                    
                    if let info = cloudService.subscriptionInfo {
                        HStack {
                            Text("\(info.usageCount)/\(info.limits.generationsPerMonth) used")
                            Spacer()
                            Text(info.subscriptionTier.capitalized)
                                .padding(.horizontal, 12)
                                .padding(.vertical, 4)
                                .background(Color.orange)
                                .cornerRadius(8)
                        }
                        .font(.caption)
                        .foregroundColor(.secondary)
                    }
                }
                .padding(.horizontal)
                
                // Input
                VStack(alignment: .leading, spacing: 8) {
                    Text("What do you need motivation for?")
                        .font(.headline)
                    
                    TextEditor(text: $userInput)
                        .frame(minHeight: 80)
                        .padding(8)
                        .background(Color.gray.opacity(0.1))
                        .cornerRadius(8)
                }
                .padding(.horizontal)
                
                // Sliders
                VStack(spacing: 20) {
                    SliderRow(title: "Intensity", value: $intensity, 
                             leftLabel: "Chill", rightLabel: "Drill Sergeant")
                    SliderRow(title: "Language", value: $languageClean,
                             leftLabel: "Raw", rightLabel: "Clean")
                    SliderRow(title: "Humor", value: $humorStyle,
                             leftLabel: "Serious", rightLabel: "Funny")
                    SliderRow(title: "Approach", value: $actionOrientation,
                             leftLabel: "Mindful", rightLabel: "Action")
                    SliderRow(title: "Length", value: $messageLength,
                             leftLabel: "Quote", rightLabel: "Speech")
                    SliderRow(title: "Music", value: $musicStyle,
                             leftLabel: "Chill", rightLabel: "Rock")
                    SliderRow(title: "Visual", value: $visualStyle,
                             leftLabel: "Still", rightLabel: "Dynamic")
                }
                .padding(.horizontal)
                
                // Generate Button
                Button(action: generateContent) {
                    if cloudService.isLoading {
                        ProgressView()
                            .progressViewStyle(CircularProgressViewStyle(tint: .white))
                    } else {
                        Text("Generate Motivation")
                    }
                }
                .frame(maxWidth: .infinity)
                .padding()
                .background(userInput.isEmpty ? Color.gray : Color.orange)
                .foregroundColor(.white)
                .cornerRadius(10)
                .disabled(cloudService.isLoading || userInput.isEmpty)
                .padding(.horizontal)
                
                // Result
                if let result = generationResult {
                    ResultView(result: result)
                        .padding(.horizontal)
                }
                
                if let error = cloudService.error {
                    Text(error)
                        .foregroundColor(.red)
                        .padding(.horizontal)
                }
            }
        }
        .background(Color.black.ignoresSafeArea())
    }
    
    private func generateContent() {
        let request = GenerationRequest(
            userInput: userInput,
            intensity: Int(intensity),
            languageClean: Int(languageClean),
            humorStyle: Int(humorStyle),
            actionOrientation: Int(actionOrientation),
            messageLength: Int(messageLength),
            musicStyle: Int(musicStyle),
            visualStyle: Int(visualStyle)
        )
        
        Task {
            let result = await cloudService.generateContent(request: request)
            DispatchQueue.main.async {
                self.generationResult = result
            }
        }
    }
}

struct SliderRow: View {
    let title: String
    @Binding var value: Double
    let leftLabel: String
    let rightLabel: String
    
    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            HStack {
                Text(title)
                    .font(.headline)
                Spacer()
                Text("\(Int(value))")
                    .foregroundColor(.orange)
                    .fontWeight(.semibold)
            }
            
            HStack {
                Text(leftLabel)
                    .font(.caption)
                    .foregroundColor(.secondary)
                
                Slider(value: $value, in: 0...100)
                    .accentColor(.orange)
                
                Text(rightLabel)
                    .font(.caption)
                    .foregroundColor(.secondary)
            }
        }
    }
}

struct ResultView: View {
    let result: GenerationResponse
    
    var body: some View {
        VStack(alignment: .leading, spacing: 15) {
            Text("Generated Content")
                .font(.headline)
            
            if let message = result.messageText {
                Text(message)
                    .padding()
                    .background(Color.gray.opacity(0.1))
                    .cornerRadius(8)
            }
            
            if result.success {
                LazyVGrid(columns: [
                    GridItem(.flexible()),
                    GridItem(.flexible())
                ], spacing: 15) {
                    if let audioUrl = result.audioUrl {
                        ContentButton(title: "Audio", icon: "play.circle", url: audioUrl)
                    }
                    if let imageUrl = result.imageUrl {
                        ContentButton(title: "Image", icon: "photo", url: imageUrl)
                    }
                    if let videoUrl = result.videoUrl {
                        ContentButton(title: "Video", icon: "video", url: videoUrl)
                    }
                }
            }
            
            if result.upgradeRequired == true {
                VStack {
                    Text("Upgrade Required")
                        .font(.headline)
                        .foregroundColor(.orange)
                    
                    NavigationLink(destination: SubscriptionView()) {
                        Text("View Plans")
                            .foregroundColor(.white)
                            .padding()
                            .background(Color.orange)
                            .cornerRadius(8)
                    }
                }
                .padding()
                .background(Color.orange.opacity(0.1))
                .cornerRadius(8)
            }
        }
    }
}

struct ContentButton: View {
    let title: String
    let icon: String
    let url: String
    
    var body: some View {
        Button(action: {
            if let url = URL(string: url) {
                UIApplication.shared.open(url)
            }
        }) {
            VStack(spacing: 8) {
                Image(systemName: icon)
                    .font(.title2)
                Text(title)
                    .font(.caption)
            }
            .frame(maxWidth: .infinity)
            .padding()
            .background(Color.orange.opacity(0.2))
            .cornerRadius(8)
        }
        .foregroundColor(.orange)
    }
}

struct SubscriptionView: View {
    @EnvironmentObject var cloudService: MotivationAICloudService
    
    var body: some View {
        ScrollView {
            VStack(spacing: 20) {
                Text("Subscription Plans")
                    .font(.largeTitle)
                    .fontWeight(.bold)
                    .padding(.top)
                
                if let info = cloudService.subscriptionInfo {
                    CurrentPlanView(info: info)
                }
                
                LazyVGrid(columns: [GridItem(.flexible()), GridItem(.flexible())], spacing: 15) {
                    PlanCard(
                        title: "Premium",
                        price: "$9.99/month",
                        features: [
                            "100 generations/month",
                            "HD video quality",
                            "Premium voices",
                            "Custom music"
                        ],
                        tier: "premium"
                    )
                    
                    PlanCard(
                        title: "Pro",
                        price: "$19.99/month",
                        features: [
                            "500 generations/month",
                            "4K video quality",
                            "All premium features",
                            "API access",
                            "Bulk generation"
                        ],
                        tier: "pro"
                    )
                }
                .padding(.horizontal)
            }
        }
        .background(Color.black.ignoresSafeArea())
        .onAppear {
            Task {
                await cloudService.loadSubscriptionInfo()
            }
        }
    }
}

struct CurrentPlanView: View {
    let info: SubscriptionInfo
    
    var body: some View {
        VStack(spacing: 10) {
            Text("Current Plan: \(info.subscriptionTier.capitalized)")
                .font(.headline)
            
            ProgressView(value: info.usagePercentage / 100)
                .progressViewStyle(LinearProgressViewStyle(tint: .orange))
            
            Text("\(info.usageCount)/\(info.limits.generationsPerMonth) generations used")
                .font(.caption)
                .foregroundColor(.secondary)
        }
        .padding()
        .background(Color.gray.opacity(0.1))
        .cornerRadius(8)
        .padding(.horizontal)
    }
}

struct PlanCard: View {
    @EnvironmentObject var cloudService: MotivationAICloudService
    let title: String
    let price: String
    let features: [String]
    let tier: String
    
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text(title)
                .font(.title2)
                .fontWeight(.bold)
            
            Text(price)
                .font(.headline)
                .foregroundColor(.orange)
            
            VStack(alignment: .leading, spacing: 4) {
                ForEach(features, id: \.self) { feature in
                    HStack {
                        Image(systemName: "checkmark")
                            .foregroundColor(.green)
                        Text(feature)
                            .font(.caption)
                    }
                }
            }
            
            Spacer()
            
            Button(action: {
                Task {
                    await cloudService.upgradeSubscription(to: tier)
                }
            }) {
                Text("Upgrade")
                    .frame(maxWidth: .infinity)
                    .padding()
                    .background(Color.orange)
                    .foregroundColor(.white)
                    .cornerRadius(8)
            }
        }
        .padding()
        .background(Color.gray.opacity(0.1))
        .cornerRadius(8)
    }
}

struct ProfileView: View {
    @EnvironmentObject var cloudService: MotivationAICloudService
    
    var body: some View {
        VStack(spacing: 20) {
            Text("Profile")
                .font(.largeTitle)
                .fontWeight(.bold)
            
            if let user = cloudService.currentUser {
                VStack(spacing: 10) {
                    Text(user.email)
                        .font(.headline)
                    
                    Text("Member since: Account created")
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
                .padding()
                .background(Color.gray.opacity(0.1))
                .cornerRadius(8)
            }
            
            Button(action: {
                cloudService.logout()
            }) {
                Text("Logout")
                    .foregroundColor(.red)
                    .padding()
                    .frame(maxWidth: .infinity)
                    .background(Color.red.opacity(0.1))
                    .cornerRadius(8)
            }
            
            Spacer()
        }
        .padding()
        .background(Color.black.ignoresSafeArea())
    }
} 