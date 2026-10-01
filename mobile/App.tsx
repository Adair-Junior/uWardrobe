import { useEffect, useState } from 'react';
import { StatusBar } from 'expo-status-bar';
import { StyleSheet, Text, View } from 'react-native';

import { getHealth } from './api/client';

export default function App() {
  const [backendStatus, setBackendStatus] = useState('Connecting to backend...');

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
  return (
    <View style={styles.container}>
      <Text>Welcome to uWardrobe 👕</Text>
      <Text>{backendStatus}</Text>
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
