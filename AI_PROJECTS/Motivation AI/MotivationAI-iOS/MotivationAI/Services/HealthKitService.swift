import HealthKit
import Foundation

class HealthKitService: ObservableObject {
    private let healthStore = HKHealthStore()
    @Published var isAuthorized = false
    @Published var todaysSteps: Double = 0
    @Published var todaysActiveEnergy: Double = 0
    @Published var todaysExerciseTime: Double = 0
    @Published var todaysWalkingDistance: Double = 0
    
    // MARK: - HealthKit Types
    private let readTypes: Set<HKObjectType> = [
        HKQuantityType.quantityType(forIdentifier: .stepCount)!,
        HKQuantityType.quantityType(forIdentifier: .activeEnergyBurned)!,
        HKQuantityType.quantityType(forIdentifier: .appleExerciseTime)!,
        HKQuantityType.quantityType(forIdentifier: .distanceWalkingRunning)!
    ]
    
    init() {
        checkAuthorizationStatus()
    }
    
    // MARK: - Authorization
    func requestAuthorization() async {
        do {
            try await healthStore.requestAuthorization(toShare: [], read: readTypes)
            await MainActor.run {
                checkAuthorizationStatus()
            }
        } catch {
            print("HealthKit authorization failed: \(error)")
        }
    }
    
    private func checkAuthorizationStatus() {
        guard HKHealthStore.isHealthDataAvailable() else {
            isAuthorized = false
            return
        }
        
        let allTypesAuthorized = readTypes.allSatisfy { type in
            healthStore.authorizationStatus(for: type) == .sharingAuthorized
        }
        
        isAuthorized = allTypesAuthorized
    }
    
    // MARK: - Data Fetching
    func fetchTodaysHealthData() async {
        guard isAuthorized else { return }
        
        let calendar = Calendar.current
        let startOfDay = calendar.startOfDay(for: Date())
        let endOfDay = calendar.date(byAdding: .day, value: 1, to: startOfDay)!
        
        await withTaskGroup(of: Void.self) { group in
            group.addTask {
                await self.fetchSteps(from: startOfDay, to: endOfDay)
            }
            group.addTask {
                await self.fetchActiveEnergy(from: startOfDay, to: endOfDay)
            }
            group.addTask {
                await self.fetchExerciseTime(from: startOfDay, to: endOfDay)
            }
            group.addTask {
                await self.fetchWalkingDistance(from: startOfDay, to: endOfDay)
            }
        }
    }
    
    private func fetchSteps(from startDate: Date, to endDate: Date) async {
        guard let stepType = HKQuantityType.quantityType(forIdentifier: .stepCount) else { return }
        
        let value = await fetchQuantitySum(for: stepType, from: startDate, to: endDate)
        await MainActor.run {
            todaysSteps = value
        }
    }
    
    private func fetchActiveEnergy(from startDate: Date, to endDate: Date) async {
        guard let energyType = HKQuantityType.quantityType(forIdentifier: .activeEnergyBurned) else { return }
        
        let value = await fetchQuantitySum(for: energyType, from: startDate, to: endDate)
        await MainActor.run {
            todaysActiveEnergy = value
        }
    }
    
    private func fetchExerciseTime(from startDate: Date, to endDate: Date) async {
        guard let exerciseType = HKQuantityType.quantityType(forIdentifier: .appleExerciseTime) else { return }
        
        let value = await fetchQuantitySum(for: exerciseType, from: startDate, to: endDate)
        await MainActor.run {
            todaysExerciseTime = value
        }
    }
    
    private func fetchWalkingDistance(from startDate: Date, to endDate: Date) async {
        guard let distanceType = HKQuantityType.quantityType(forIdentifier: .distanceWalkingRunning) else { return }
        
        let value = await fetchQuantitySum(for: distanceType, from: startDate, to: endDate)
        await MainActor.run {
            todaysWalkingDistance = value
        }
    }
    
    private func fetchQuantitySum(for quantityType: HKQuantityType, from startDate: Date, to endDate: Date) async -> Double {
        return await withCheckedContinuation { continuation in
            let predicate = HKQuery.predicateForSamples(withStart: startDate, end: endDate)
            
            let query = HKStatisticsQuery(
                quantityType: quantityType,
                quantitySamplePredicate: predicate,
                options: .cumulativeSum
            ) { _, result, error in
                guard let result = result,
                      let sum = result.sumQuantity() else {
                    continuation.resume(returning: 0.0)
                    return
                }
                
                let unit = self.getUnit(for: quantityType)
                let value = sum.doubleValue(for: unit)
                continuation.resume(returning: value)
            }
            
            healthStore.execute(query)
        }
    }
    
    private func getUnit(for quantityType: HKQuantityType) -> HKUnit {
        switch quantityType.identifier {
        case HKQuantityTypeIdentifier.stepCount.rawValue:
            return HKUnit.count()
        case HKQuantityTypeIdentifier.activeEnergyBurned.rawValue:
            return HKUnit.kilocalorie()
        case HKQuantityTypeIdentifier.appleExerciseTime.rawValue:
            return HKUnit.minute()
        case HKQuantityTypeIdentifier.distanceWalkingRunning.rawValue:
            return HKUnit.meter()
        default:
            return HKUnit.count()
        }
    }
    
    // MARK: - Task Completion Helpers
    func checkFitnessTaskCompletion(for integration: FitnessIntegration) -> Bool {
        guard let healthKitType = integration.healthKitType else { return false }
        
        switch healthKitType {
        case .stepCount:
            return todaysSteps >= integration.targetValue
        case .activeEnergyBurned:
            return todaysActiveEnergy >= integration.targetValue
        case .appleExerciseTime:
            return todaysExerciseTime >= integration.targetValue
        case .distanceWalkingRunning:
            return todaysWalkingDistance >= integration.targetValue
        default:
            return false
        }
    }
    
    func getFitnessProgress(for integration: FitnessIntegration) -> Double {
        guard let healthKitType = integration.healthKitType else { return 0.0 }
        
        let currentValue: Double
        
        switch healthKitType {
        case .stepCount:
            currentValue = todaysSteps
        case .activeEnergyBurned:
            currentValue = todaysActiveEnergy
        case .appleExerciseTime:
            currentValue = todaysExerciseTime
        case .distanceWalkingRunning:
            currentValue = todaysWalkingDistance
        default:
            currentValue = 0
        }
        
        return min(1.0, currentValue / integration.targetValue)
    }
    
    func getFitnessData(for integration: FitnessIntegration) -> FitnessData? {
        guard let healthKitType = integration.healthKitType else { return nil }
        
        let currentValue: Double
        
        switch healthKitType {
        case .stepCount:
            currentValue = todaysSteps
        case .activeEnergyBurned:
            currentValue = todaysActiveEnergy
        case .appleExerciseTime:
            currentValue = todaysExerciseTime
        case .distanceWalkingRunning:
            currentValue = todaysWalkingDistance
        default:
            return nil
        }
        
        return FitnessData(
            value: currentValue,
            unit: integration.unitString,
            recordedAt: Date(),
            source: "HealthKit"
        )
    }
} 