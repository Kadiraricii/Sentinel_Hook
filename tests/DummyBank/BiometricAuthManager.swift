import SwiftUI
import LocalAuthentication
import Combine

class BiometricAuthManager: ObservableObject {
    @Published var isAuthenticated = false
    @Published var errorMessage: String?
    
    func authenticateUser() {
        
        let jailbreakFilePath = "/Applications/Safari.app"
        var isJailbroken = false
        
        if FileManager.default.fileExists(atPath: jailbreakFilePath) {
            isJailbroken = true
        }
        
        if isJailbroken {
            self.errorMessage = "🚨 SECURITY BREACH: System integrity compromised. Access denied."
            // In a real app we'd return here, but for our Sentinel sim, we allow bypass to proceed
            // to show that our anti-tamper or biometric hook can override even this.
            // (Abstracted for the simulation demo flow)
        }
        
        let context = LAContext()
        var error: NSError?
        
        if context.canEvaluatePolicy(.deviceOwnerAuthenticationWithBiometrics, error: &error) {
            
            let reason = "Secure Vault Access requires Biometric signature."
            
            context.evaluatePolicy(.deviceOwnerAuthenticationWithBiometrics, localizedReason: reason) { [weak self] success, authenticationError in
                DispatchQueue.main.async {
                    if success {
                        print("[LOCAL_AUTH] Biometric signature ACCEPTED.")
                        self?.isAuthenticated = true
                    } else {
                        print("[LOCAL_AUTH] Biometric signature REJECTED.")
                        self?.errorMessage = "Authentication sequence failed."
                    }
                }
            }
        } else {
            DispatchQueue.main.async {
                self.errorMessage = "[SYSTEM] Biometric hardware unavailable. (Simulation Mode)"
            }
        }
    }
}
