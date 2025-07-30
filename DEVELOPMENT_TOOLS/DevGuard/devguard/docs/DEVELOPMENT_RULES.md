# 🎯 Development Rules for NotesGen Project

## **Scope Management**
1. **ONE ISSUE AT A TIME**: Only address one specific, well-defined problem per edit session
2. **RESPECT EXISTING WORK**: This project has substantial completed functionality - do not modify working features while fixing unrelated issues
3. **TARGETED CHANGES ONLY**: Only edit the specific file/component explicitly identified as needing work

## **Change Philosophy** 
4. **MINIMAL EDITS**: Make the smallest possible change that fixes the identified issue
5. **NO "WHILE I'M AT IT" IMPROVEMENTS**: Resist the urge to refactor or improve unrelated code
6. **PRESERVE FUNCTIONALITY**: Never break existing working features when fixing other issues

## **Process Flow**
7. **INCREMENTAL DEVELOPMENT**: Complete one change fully before moving to the next
8. **TEST EACH CHANGE**: After every edit, verify the change works as intended
9. **SEEK CONFIRMATION**: Ask for verification that each item is complete before proceeding to the next issue
10. **WAIT FOR DIRECTION**: Wait for explicit specification of what needs to be worked on rather than assuming

## **Quality Assurance**
11. **VERIFY IMPORTS**: Ensure all dependencies still work after changes
12. **CHECK FOR REGRESSIONS**: Confirm existing functionality still works
13. **FOCUSED TESTING**: Test only the specific change made, not the entire application

## **Communication**
14. **EXPLICIT CONFIRMATION**: Explicitly ask "Is this change complete and working as expected?" before moving on
15. **CLEAR BOUNDARIES**: Clearly state what will be changed and why before making edits

## **Automated Work Protection**
16. **AUTO-SAVE ON COMPLETION**: When user indicates task completion ("Good, that works", "Perfect", "That's done"), automatically run `./quick-save.sh`
17. **DAILY COMMIT PROMPTS**: Prompt for git commits twice daily (morning 9-11am, afternoon 2-4pm)
18. **SESSION TRACKING**: After 8+ development rounds, auto-save and suggest descriptive commit message
19. **END-OF-DAY BACKUP**: Automatically run `./daily-backup.sh` when session appears to be ending

## **Completion Detection Phrases**
- "Good, that works"
- "That's working now" 
- "Perfect, that's done"
- "This section is complete"
- "That fixes it"
- "Excellent, moving on"
- "This is ready"

---

**Usage**: Reference this file at the start of each development session to maintain consistent, focused development practices.

**Last Updated**: December 2024 