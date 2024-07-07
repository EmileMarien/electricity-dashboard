  

"""
firebase_auth.User? firebaseUser;
housekeeper.User? customUser;

class AuthenticationRepository {
  final firebase_auth.FirebaseAuth _auth = firebase_auth.FirebaseAuth.instance;

  //add authRepositoryProvider

  housekeeper.User? _housekeeperUser(firebase_auth.User? user) { //map Firebase User into our model properties
      return user != null ? housekeeper.User(referenceId: user.uid,email: user.email) : null;
    }

  Stream<housekeeper.User?> get user { //check whenever FirbaseAuth Changes
      return _auth.authStateChanges().map(_housekeeperUser);
    }

  Future signInEmailPassword(housekeeper.User _login) async {
    try {
      firebase_auth.UserCredential userCredential = await firebase_auth.FirebaseAuth.instance
          .signInWithEmailAndPassword(
              email: _login.email.toString(),
              password: _login.password.toString());
      firebase_auth.User? user = userCredential.user;
      return _housekeeperUser(user);
    } on firebase_auth.FirebaseAuthException catch (e) {
      return housekeeper.User(code: e.code, referenceId: null);
    }
  }

  Future signInWithGoogle() async {
    try {
      // Create an instance of GoogleSignIn
      final GoogleSignIn googleSignIn = GoogleSignIn();

      // Trigger Google Sign-In process
      final GoogleSignInAccount? googleUser = await googleSignIn.signIn();

      // If user canceled the sign-in process or something went wrong
      if (googleUser == null) {
        return null; // Return null or handle the cancellation/error scenario as needed
      }

      // If sign-in is successful, get GoogleSignInAuthentication
      final GoogleSignInAuthentication googleAuth = await googleUser.authentication;

      // Use GoogleSignInAuthentication to authenticate with Firebase
      final firebase_auth.AuthCredential credential = firebase_auth.GoogleAuthProvider.credential(
        accessToken: googleAuth.accessToken,
        idToken: googleAuth.idToken,
      );

      // Sign in to Firebase using the credential
      final firebase_auth.UserCredential userCredential = await firebase_auth.FirebaseAuth.instance.signInWithCredential(credential);

      // Get the user object from UserCredential
      firebase_auth.User? user = userCredential.user;

      return user;
    } catch (e) {
    print("Google Sign-In Error: $e");
    return null;
    }
  }

  Future registerEmailPassword(housekeeper.User _login) async {
    try {
      firebase_auth.UserCredential userCredential = await _auth.createUserWithEmailAndPassword(
              email: _login.email.toString(),
              password: _login.password.toString());
      firebase_auth.User? user = userCredential.user;
      return _housekeeperUser(user);
    } on firebase_auth.FirebaseAuthException catch (e) {
      return housekeeper.User(code: e.code, referenceId: null);
    } catch (e) {
      return housekeeper.User(code: e.toString(), referenceId: null);
    }
  }

  Future signOutGoogle() async{}

  Future getUser() async {}

  Future signOut() async {
      try {
        return await _auth.signOut();
      } catch (e) {
        return null;
      }
    }
}
"""