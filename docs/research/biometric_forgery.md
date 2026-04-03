This script targets the two primary layers of iOS security: **Data-at-Rest Protection (Keychain)** and **Runtime Identity Verification (LocalAuthentication/Biometrics).**

By neutralizing these, an attacker or researcher can access protected secrets (like OAuth tokens, passwords, or private keys) without needing the user's face, fingerprint, or passcode.

Here is the technical breakdown of how these bypasses function.

---

### 1. Stripping the Keychain ACL (`SecItemCopyMatching`)

When an app developer wants to store a sensitive item in the Keychain, they often add an **Access Control List (ACL)** using the attribute `kSecAttrAccessControl`. This attribute tells the iOS Secure Enclave: *"Do not release this secret unless the user successfully performs a FaceID/TouchID scan."*

#### The Logic of the Bypass:
1.  **Interception:** The script hooks `SecItemCopyMatching`, which is the standard C function used to query the Keychain.
2.  **Detection:** Inside `onEnter`, it looks at the search query (a `CFDictionary` passed as `args[0]`). It searches for the key `kSecAttrAccessControl`. 
3.  **Dictionary Tampering:** 
    *   Because the original query dictionary is often immutable, the script calls `CFDictionaryCreateMutableCopy`.
    *   It then uses `CFDictionaryRemoveValue` to delete the `kSecAttrAccessControl` key from the copy.
4.  **Parameter Swapping:** The script replaces the original pointer in `args[0]` with its own "patched" dictionary.
5.  **The Result:** When the real `SecItemCopyMatching` executes, it sees a request that says: *"Give me the password, and by the way, there are no biometric requirements for this search."* The system then hands over the secret without ever triggering the iOS biometric popup.

---

### 2. Biometric Logic Bypass (`LAContext`)

Even if the Keychain is bypassed, the app might have a secondary logic gate: a "Login" button that triggers a FaceID prompt via the `LocalAuthentication` framework. If that prompt fails, the app doesn't let you in. This script targets the `LAContext` class to simulate a "Success" state.

#### Phase A: Capability Faking (`canEvaluatePolicy`)
Before an app even tries to show a FaceID prompt, it usually asks: *"Is biometrics even available on this phone?"*
*   The script hooks `- canEvaluatePolicy:error:`.
*   In `onLeave`, it forces the return value to `ptr(1)` (True).
*   **Result:** The app is tricked into believing FaceID is set up and functional, even on a simulator or a broken device.

#### Phase B: Asynchronous Result Forging (`evaluatePolicy...reply:`)
The actual biometric prompt is asynchronous. The app calls `evaluatePolicy` and provides a **Reply Block** (a callback function) that executes once the user scans their face.

*   **The Hook:** The script intercepts the call to `- evaluatePolicy:localizedReason:reply:`.
*   **Block Redirection:** The 5th argument (`args[4]`) is the `reply` block. The script creates a *new* `ObjC.Block`.
*   **The Forgery:** Inside this new block's implementation, it immediately calls the **original** block but hardcodes the arguments:
    *   `success` = `true`
    *   `error` = `NULL`
*   **The Result:** The moment the app tries to show the FaceID prompt, the script's "fake" block fires instantly. The app's logic receives a "Success" message and proceeds to the "Logged In" state without the user ever seeing a FaceID animation.

---

### Summary of the "Attack" Flow

| Component | Target | Action | Outcome |
| :--- | :--- | :--- | :--- |
| **Keychain** | `SecItemCopyMatching` | Removes `kSecAttrAccessControl` | The Secure Enclave releases the secret without requiring a biometric unlock. |
| **Biometrics** | `canEvaluatePolicy` | Forces return to `True` | App logic believes the device is capable of biometric auth. |
| **Biometrics** | `LAContext reply block` | Forges `Success=YES` | The app's "Access Granted" code executes immediately, bypassing the UI prompt. |

### Why this is effective:
This script performs **Parameter Tampering** and **Callback Redirection**. It doesn't actually "crack" the encryption of the Keychain; instead, it manipulates the API calls so that the OS itself decides that authentication is either unnecessary (Keychain) or has already successfully occurred (LAContext).