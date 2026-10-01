import { useEffect, useState } from 'react';
import { StatusBar } from 'expo-status-bar';
import { Button, StyleSheet, Text, View } from 'react-native';

import { 
  getCurrentUser, 
  getHealth,
  loginUser, 
  registerUser,
} from './api/client';

export default function App() {
  const [backendStatus, setBackendStatus] = useState('Connecting to backend...');

  const [registrationStatus, setRegistrationStatus] = useState(
    'Registration not tested'
  );
  const [loginStatus, setLoginStatus] = useState(
    'Login not tested'
  );

  const [accessToken, setAccessToken] = useState<string | null>(null);

  const [currentUserStatus, setCurrentUserStatus] = useState(
    'Current user not tested'
  );

  useEffect(() => {
    getHealth()
      .then((data) => {
        console.log('Backend response:', data);
        setBackendStatus(`Backend status: ${data.status}`);
      })
      .catch((error) => {
        console.error('Backend connection failed:', error);
        setBackendStatus('Backend connection failed');
      });
  }, []);

  const testRegistration = async () => {
    try {
      setRegistrationStatus('Registering...');

      const user = await registerUser({
        email: 'day24test@uwardrobe.app',
        password: 'TestPassword123!',
      });

      console.log('Registered user:', user);
      setRegistrationStatus(`Registered: ${user.email}`);
    } catch (error) {
      console.error('Registration failed:', error);
      setRegistrationStatus('Registration failed');
    }
  };

  const testLogin = async () => {
    try {
      const data = await loginUser({
        email: 'day24test@uwardrobe.app',
        password: 'TestPassword123!',
      });

      setAccessToken(data.access_token);

      console.log('Logged in:', data);
      setLoginStatus(`Logged in successfully`);
    } catch (error) {
      console.error('Login failed:', error);
      setLoginStatus('Login failed');
    }
  };

  const testCurrentUser = async () => {
    if (!accessToken) {
      setCurrentUserStatus('Please log in first');
      return;
    }

    try {
      const user = await getCurrentUser(accessToken);

      console.log('Current user:', user);
      setCurrentUserStatus(`Current user: ${user.email}`);
    } catch (error) {
      console.error('Current user failed:', error);
      setCurrentUserStatus(`Current user failed: ${String(error)}`);
    }
  };

  const testUnauthorizedUser = async () => {
    try {
      await getCurrentUser('invalid-token');

      setCurrentUserStatus('ERROR: Invalid token was accepted');
    } catch (error) {
      console.log('Unauthorized request correctly rejected');
      setCurrentUserStatus('Invalid token correctly rejected');
    }
  };

  return (
    <View style={styles.container}>
      <Text>Welcome to uWardrobe 👕</Text>
      <Text>{backendStatus}</Text>
      <Text>{registrationStatus}</Text>
      <Text>{loginStatus}</Text>
      <Text>{currentUserStatus}</Text>

      <Button
        title="Test Registration"
        onPress={testRegistration}
      />

      <Button
        title="Test Login"
        onPress={testLogin}
      />

      <Button
        title="Test Current User"
        onPress={testCurrentUser}
      />

      <Button
        title="Test Invalid Token"
        onPress={testUnauthorizedUser}
      />

      <StatusBar style="auto" />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
    alignItems: 'center',
    justifyContent: 'center',
  },
});
