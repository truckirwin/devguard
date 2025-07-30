import Foundation
import Combine

// MARK: - Data Models

struct AIMessageResponse: Codable {
    let messageText: String
    let style: String
    let musicStyle: String
    let visualStyle: String
    let backgroundImage: String
    let audioFile: String?
    let success: Bool
    let demoMode: Bool?
    
    enum CodingKeys: String, CodingKey {
        case messageText = "message_text"
        case style
        case musicStyle = "music_style"
        case visualStyle = "visual_style"
        case backgroundImage = "background_image"
        case audioFile = "audio_file"
        case success
        case demoMode = "demo_mode"
    }
}

struct AIMessageError: Codable {
    let error: String
    let message: String?
    let success: Bool
}

// MARK: - Service

class AIMessageService: ObservableObject {
    static let shared = AIMessageService()
    
    private let baseURL = "http://localhost:8080" // Change this to your server's URL
    private let session = URLSession.shared
    
    private init() {}
    
    func generateMessage(preferences: [String: Any], completion: @escaping (Result<AIMessageResponse, Error>) -> Void) {
        guard let url = URL(string: "\(baseURL)/demo") else {
            completion(.failure(AIServiceError.invalidURL))
            return
        }
        
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        do {
            let jsonData = try JSONSerialization.data(withJSONObject: preferences)
            request.httpBody = jsonData
        } catch {
            completion(.failure(AIServiceError.encodingError))
            return
        }
        
        session.dataTask(with: request) { data, response, error in
            if let error = error {
                completion(.failure(error))
                return
            }
            
            guard let data = data else {
                completion(.failure(AIServiceError.noData))
                return
            }
            
            // First try to decode as success response
            do {
                let messageResponse = try JSONDecoder().decode(AIMessageResponse.self, from: data)
                completion(.success(messageResponse))
            } catch {
                // If that fails, try to decode as error response
                do {
                    let errorResponse = try JSONDecoder().decode(AIMessageError.self, from: data)
                    completion(.failure(AIServiceError.serverError(errorResponse.error)))
                } catch {
                    completion(.failure(AIServiceError.decodingError))
                }
            }
        }.resume()
    }
    
    func testConnection(completion: @escaping (Bool) -> Void) {
        guard let url = URL(string: "\(baseURL)/api/test") else {
            completion(false)
            return
        }
        
        session.dataTask(with: URLRequest(url: url)) { data, response, error in
            DispatchQueue.main.async {
                completion(error == nil && data != nil)
            }
        }.resume()
    }
}

// MARK: - Error Handling

enum AIServiceError: LocalizedError {
    case invalidURL
    case encodingError
    case decodingError
    case noData
    case serverError(String)
    
    var errorDescription: String? {
        switch self {
        case .invalidURL:
            return "Invalid server URL"
        case .encodingError:
            return "Failed to encode request data"
        case .decodingError:
            return "Failed to decode server response"
        case .noData:
            return "No data received from server"
        case .serverError(let message):
            return "Server error: \(message)"
        }
    }
}

// MARK: - Combine Support (Optional)

extension AIMessageService {
    func generateMessagePublisher(preferences: [String: Any]) -> AnyPublisher<AIMessageResponse, Error> {
        Future { promise in
            self.generateMessage(preferences: preferences) { result in
                promise(result)
            }
        }
        .eraseToAnyPublisher()
    }
} 