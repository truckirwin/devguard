import Foundation

struct DemoVideoScripts {
    
    // MARK: - Demo Scripts from Rise and Grind Messages
    static let demoScripts = [
        // Morning Energy - "Rise Up, Job Hunter"
        MotivationalMessage(
            id: "rise_up_job_hunter",
            title: "Wake The Fck UP!",
            content: "WAKE THE F*CK UP, FUTURE CEO! Yeah, you heard me right! That last job didn't work out? SO F*CKING WHAT! That wasn't your destination - that was just a pit stop on your way to GREATNESS! Today's task list is sitting there waiting for you like a loyal soldier! Those applications won't submit themselves! Those networking calls won't make themselves! That LinkedIn profile won't optimize itself! You think successful people got where they are by hitting snooze? HELL NO! They got up every morning knowing that THEIR FUTURE DEPENDED ON THEIR HUSTLE! Your dream job is out there RIGHT NOW wondering where the hell you are! Stop keeping it waiting! Get up, get caffeinated, and GET HUNTING! Today's the day you turn rejection into REDIRECTION!",
            author: nil,
            category: .morningWakeUp,
            timeOfDay: .morning,
            tone: .energetic,
            backgroundImageName: "dawn_mountain_valley",
            audioEnabled: true,
            duration: 60,
            actionPrompt: "Get Hunting!"
        ),
        
        // Morning Power - "Hunt Mode Activated"
        MotivationalMessage(
            id: "hunt_mode_activated",
            title: "Hunt Mode Activated",
            content: "WAKE UP, YOU RELENTLESS CAREER HUNTER! The corporate jungle is full of opportunities, but they don't come to the LAZY! They come to the HUNGRY! And you? You're F*CKING STARVING for success! That task list isn't suggestions - it's MARCHING ORDERS! Every job board you hit is territory you're claiming! Every application you perfect is ammunition you're loading! Being between jobs doesn't make you unemployed - it makes you AVAILABLE for something AMAZING! You're not looking for work - you're shopping for your NEXT KINGDOM! Get up and show this day what happens when someone REFUSES to stay down! Your future employer is out there wondering where their STAR PLAYER is! TIME TO HUNT!",
            author: nil,
            category: .morningWakeUp,
            timeOfDay: .morning,
            tone: .toughLove,
            backgroundImageName: "runner_distance",
            audioEnabled: true,
            duration: 60,
            actionPrompt: "Time to Hunt!"
        ),
        
        // Midday Momentum - "Momentum Machine"
        MotivationalMessage(
            id: "momentum_machine",
            title: "Momentum Machine",
            content: "MIDDAY CHECK-IN, YOU MAGNIFICENT MOMENTUM MACHINE! Look at you GO! Morning tasks getting CRUSHED! But don't you dare slow down now! This is where champions separate themselves from the wannabes! You've got momentum building - that's PURE F*CKING GOLD in the job search game! Every application sent this morning is working for you RIGHT NOW! Every connection made is opening doors! The afternoon isn't time to coast - it's time to ACCELERATE! Those remaining tasks are waiting for their turn to get DEMOLISHED! Your future employer is probably reviewing applications right now! Make sure yours is the one that makes them say 'HOLY SH*T, we need to meet this person!' DON'T STOP NOW - DOMINATE THE REST!",
            author: nil,
            category: .midDayCheckIn,
            timeOfDay: .midday,
            tone: .energetic,
            backgroundImageName: "winding_road",
            audioEnabled: true,
            duration: 60,
            actionPrompt: "Dominate the Rest!"
        ),
        
        // Afternoon Power - "Closing Time Crusher"
        MotivationalMessage(
            id: "closing_time_crusher",
            title: "Closing Time Crusher",
            content: "AFTERNOON FINAL PUSH, YOU CLOSING-TIME CRUSHER! This is it! The final stretch! The moment that separates FINISHERS from quitters! You didn't come this far to only come this f*cking far! Those last few tasks aren't just items on a list - they're the difference between a good day and a LEGENDARY day! Between progress and BREAKTHROUGH! Every successful person knows the secret: it's not how you start - it's how you FINISH! And you? You finish like a F*CKING CHAMPION! Your future self is watching this moment! Are you going to be the person who gave their ALL, or the one who gave up when it got tough? CLOSE THIS DAY LIKE THE WINNER YOU ARE!",
            author: nil,
            category: .actionOriented,
            timeOfDay: .afternoon,
            tone: .toughLove,
            backgroundImageName: "canyon_vista",
            audioEnabled: true,
            duration: 60,
            actionPrompt: "Finish Strong!"
        ),
        
        // Evening Victory - "Victory Reflection"
        MotivationalMessage(
            id: "victory_reflection",
            title: "Victory Reflection",
            content: "DAY IS DONE, YOU MAGNIFICENT WARRIOR! Look what you f*cking ACCOMPLISHED today! Tasks completed, connections made, opportunities created! You didn't just survive another day of job searching - you DOMINATED it! Every application sent is working for you while you sleep! Every skill improved is making you MORE valuable! Every connection made is opening doors you can't even see yet! Tomorrow's going to bring new challenges, but tonight? Tonight you REST like someone who EARNED it! You fought the good fight and you WON! Your comeback story got another chapter written today! And it was a BADASS chapter! SLEEP LIKE THE CHAMPION YOU ARE!",
            author: nil,
            category: .eveningWindDown,
            timeOfDay: .evening,
            tone: .compassionate,
            backgroundImageName: "starry_night",
            audioEnabled: true,
            duration: 60,
            actionPrompt: "Rest Like a Champion!"
        ),
        
        // NEW MESSAGES - LinkedIn Focus
        MotivationalMessage(
            id: "linkedin_warrior",
            title: "LinkedIn Warrior",
            content: "Time to DOMINATE LinkedIn like the professional BEAST you are! Your profile isn't just a resume - it's your PERSONAL BRAND HEADQUARTERS! Every connection request you send is building your empire! Every thoughtful comment you make is showing your expertise! Every article you share positions you as a THOUGHT LEADER! Stop scrolling and start HUNTING! Search for people in your target companies! Send connection requests with PERSONAL messages! Comment on posts in your industry! Your next job is hiding in someone's LinkedIn network - GO FIND IT! Make LinkedIn your full-time job until you GET your full-time job!",
            author: nil,
            category: .linkedInFocus,
            timeOfDay: .anytime,
            tone: .actionFocused,
            backgroundImageName: "city_skyline",
            audioEnabled: true,
            duration: 45,
            actionPrompt: "Dominate LinkedIn!"
        ),
        
        // Rejection Recovery
        MotivationalMessage(
            id: "rejection_rocket_fuel",
            title: "Rejection = Rocket Fuel",
            content: "Got rejected? GOOD! You know what rejection really is? It's ROCKET FUEL for your comeback story! Every 'no' gets you closer to your YES! Every rejection means you're PUTTING YOURSELF OUT THERE while others sit on the sidelines! You think every successful person got their dream job on the first try? HELL NO! They got rejected, dusted themselves off, and came back STRONGER! That rejection isn't about you - it's about FIT! And guess what? You don't want to work somewhere that doesn't recognize your GREATNESS anyway! Use this energy! Apply to 5 more companies TODAY! Show the universe that you DON'T take no for an answer!",
            author: nil,
            category: .rejectionRecovery,
            timeOfDay: .anytime,
            tone: .inspiring,
            backgroundImageName: "volcano_landscape",
            audioEnabled: true,
            duration: 50,
            actionPrompt: "Bounce Back Stronger!"
        ),
        
        // Compassionate Morning
        MotivationalMessage(
            id: "gentle_morning_strength",
            title: "Your Gentle Morning Strength",
            content: "Good morning, beautiful human. I know this job search feels overwhelming sometimes. I know you're tired of putting yourself out there, of writing cover letters, of wondering if you're good enough. But let me remind you of something important: YOU ARE ENOUGH. Exactly as you are right now. This transition period? It's not punishment - it's preparation. Every skill you're building, every connection you're making, every interview you're having is preparing you for something AMAZING. Today, be gentle with yourself AND productive. One small step forward is still progress. You don't have to conquer the world today - just take the next right step. You've got this, and I believe in you.",
            author: nil,
            category: .morningWakeUp,
            timeOfDay: .morning,
            tone: .compassionate,
            backgroundImageName: "spring_blossoms",
            audioEnabled: true,
            duration: 55,
            actionPrompt: "Take the Next Step"
        ),
        
        // Interview Prep Power
        MotivationalMessage(
            id: "interview_warrior",
            title: "Interview Warrior Mode",
            content: "INTERVIEW COMING UP? Time to activate WARRIOR MODE! You didn't get this interview by accident - they CHOSE YOU out of hundreds of applications! They already think you can do the job - now you just need to show them your personality and passion! Research that company like you're writing a biography! Know their recent wins, their challenges, their culture! Prepare stories that show your impact - use the STAR method! Practice your answers out loud until they flow naturally! Remember: they need YOU as much as you need them! Walk in there knowing you're interviewing THEM too! You're not begging for a job - you're exploring a PARTNERSHIP! Show them the confident, capable professional you ARE!",
            author: nil,
            category: .interviewPrep,
            timeOfDay: .anytime,
            tone: .professional,
            backgroundImageName: "urban_dawn",
            audioEnabled: true,
            duration: 65,
            actionPrompt: "Prepare to Dominate!"
        ),
        
        // Network Building
        MotivationalMessage(
            id: "networking_ninja",
            title: "Networking Ninja",
            content: "Time to become a NETWORKING NINJA! Your network is your NET WORTH in this job market! Every person you meet is a potential door to your future! Stop thinking networking is 'using people' - it's about building GENUINE RELATIONSHIPS! Start with people you already know - former colleagues, classmates, neighbors! Ask for advice, not jobs! People LOVE giving advice! Join professional groups, attend virtual events, comment meaningfully on LinkedIn posts! Remember: networking isn't about what others can do for you - it's about building a community where everyone WINS! Be generous, be authentic, be interested in others! Your next opportunity might come from someone you help TODAY!",
            author: nil,
            category: .networkBuilding,
            timeOfDay: .anytime,
            tone: .professional,
            backgroundImageName: "meadow_flowers",
            audioEnabled: true,
            duration: 60,
            actionPrompt: "Build Connections!"
        ),
        
        // Friday Motivation
        MotivationalMessage(
            id: "friday_finish_strong",
            title: "Friday Finish Strong",
            content: "IT'S FRIDAY, YOU MAGNIFICENT FINISHER! While others are mentally checking out, you're about to SEPARATE YOURSELF from the pack! This is your competitive advantage moment! When they're thinking about happy hour, you're thinking about your FUTURE HOUR! Use this Friday energy to do what others won't: follow up on applications, send those networking messages, update your LinkedIn! Hiring managers are still working, recruiters are still recruiting, opportunities are still flowing! Don't let Friday be your excuse - let it be your FUEL! Finish this week like the CHAMPION you are! Monday's success starts with Friday's HUSTLE!",
            author: nil,
            category: .fridayMotivation,
            timeOfDay: .afternoon,
            tone: .energetic,
            backgroundImageName: "golden_fields",
            audioEnabled: true,
            duration: 50,
            actionPrompt: "Finish Strong!"
        ),
        
        // Monday Energy
        MotivationalMessage(
            id: "monday_momentum",
            title: "Monday Momentum Builder",
            content: "MONDAY MEANS MOMENTUM, YOU BEAUTIFUL CAREER CRUSHER! While everyone else has the Monday blues, you've got the Monday ROCKET FUEL! This is your RESET button! Your fresh start! Your chance to build momentum that carries through the ENTIRE WEEK! New jobs were posted over the weekend! New networking opportunities are waiting! New connections are ready to be made! You're not just starting another week - you're starting another chapter of your COMEBACK STORY! Set your intentions, plan your attacks, and execute with PRECISION! This Monday isn't just the start of your week - it's the start of your BREAKTHROUGH!",
            author: nil,
            category: .mondayEnergy,
            timeOfDay: .morning,
            tone: .energetic,
            backgroundImageName: "mountain_sunrise",
            audioEnabled: true,
            duration: 55,
            actionPrompt: "Build Momentum!"
        )
    ]
    
    // MARK: - Helper Functions
    static func getScriptsByTimeOfDay(_ timeOfDay: TimeOfDay) -> [MotivationalMessage] {
        return demoScripts.filter { $0.timeOfDay == timeOfDay || timeOfDay == .anytime }
    }
    
    static func getRandomScript() -> MotivationalMessage {
        return demoScripts.randomElement() ?? demoScripts[0]
    }
    
    static func getMorningDemos() -> [MotivationalMessage] {
        return demoScripts.filter { $0.timeOfDay == .morning }
    }
    
    static func getMiddayDemos() -> [MotivationalMessage] {
        return demoScripts.filter { $0.timeOfDay == .midday }
    }
    
    static func getAfternoonDemos() -> [MotivationalMessage] {
        return demoScripts.filter { $0.timeOfDay == .afternoon }
    }
    
    static func getEveningDemos() -> [MotivationalMessage] {
        return demoScripts.filter { $0.timeOfDay == .evening }
    }
    
    static func getScriptById(_ id: String) -> MotivationalMessage? {
        return demoScripts.first { $0.id == id }
    }
    
    // MARK: - All Demo Scripts
    static let allDemoScripts = demoScripts
    
    // MARK: - Filtered Scripts by Tone
    static var toughLoveScripts: [MotivationalMessage] {
        return demoScripts.filter { $0.tone == .toughLove }
    }
}

// MARK: - Word Count Verification
extension MotivationalMessage {
    var wordCount: Int {
        return content.components(separatedBy: .whitespacesAndNewlines)
            .filter { !$0.isEmpty }
            .count
    }
    
    var estimatedReadingTime: Double {
        // Average speaking rate: 150-160 words per minute
        return Double(wordCount) / 150.0 * 60.0 // Convert to seconds
    }
    
    var isDemo: Bool {
        return DemoVideoScripts.demoScripts.contains { $0.id == self.id }
    }
} 