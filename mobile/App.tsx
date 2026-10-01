import { useEffect, useState } from 'react';
import { StatusBar } from 'expo-status-bar';
import { Button, StyleSheet, Text, View } from 'react-native';

import { 
  ClothingItem,
  createClothingItem,
  deleteClothingItem,
  getCurrentUser, 
  getHealth,
  getWardrobe,
  loginUser, 
  registerUser,
  updateClothingItem,
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

  const [wardrobeStatus, setWardrobeStatus] = useState(
    'Wardrobe not loaded'
  );

  const [wardrobeItems, setWardrobeItems] = useState<ClothingItem[]>([]);

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

  const testWardrobe = async () => {
    if (!accessToken) {
      setWardrobeStatus('Please log in first');
      return;
    }

    try {
      const items = await getWardrobe(accessToken);

      setWardrobeItems(items);

      console.log('Wardrobe:', items);
      setWardrobeStatus(`Wardrobe loaded: ${items.length} item(s)`);
    } catch (error) {
      console.error('Wardrobe failed:', error);
      setWardrobeStatus(`Wardrobe failed: ${String(error)}`);
    }
  };

  const testCreateClothingItem = async () => {
    if (!accessToken) {
      setWardrobeStatus('Please log in first');
      return;
    }

    try {
      const item = await createClothingItem(accessToken, {
        name: 'Black T-Shirt',
        category: 'top',
        color: 'black',
        style: 'casual',
        season: 'all-season',
      });

      console.log('Created clothing item:', item);
      setWardrobeStatus(`Created: ${item.name}`);
    } catch (error) {
      console.error('Create clothing item failed:', error);
      setWardrobeStatus(`Create failed: ${String(error)}`);
    }
  };

  const handleDeleteClothingItem = async (itemId: string) => {
    if (!accessToken) {
      setWardrobeStatus('Please log in first');
      return;
    }

    try {
      await deleteClothingItem(accessToken, itemId);

      setWardrobeItems((currentItems) =>
        currentItems.filter((item) => item.id !== itemId)
      );

      setWardrobeStatus('Clothing item deleted');
    } catch (error) {
      console.error('Delete clothing item failed:', error);
      setWardrobeStatus(`Delete failed: ${String(error)}`);
    }
  };

  const handleUpdateClothingItem = async (item: ClothingItem) => {
    if (!accessToken) {
      setWardrobeStatus('Please log in first');
      return;
    }

    try {
      const updatedItem = await updateClothingItem(
        accessToken,
        item.id,
        {
          name: `${item.name} Updated`,
          category: item.category,
          color: item.color,
          style: item.style,
          season: item.season,
        }
      );

      setWardrobeItems((currentItems) =>
        currentItems.map((currentItem) =>
          currentItem.id === updatedItem.id ? updatedItem : currentItem
        )
      );

      setWardrobeStatus(`Updated: ${updatedItem.name}`);
    } catch (error) {
      console.error('Update clothing item failed:', error);
      setWardrobeStatus(`Update failed: ${String(error)}`);
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
      <Text>{wardrobeStatus}</Text>

      {wardrobeItems.map((item) => (
        <View key={item.id}>
          <Text>{item.name}</Text>
          <Text>
            {item.category} | {item.color} | {item.style} | {item.season}
          </Text>

          <Button
            title="Update"
            onPress={() => handleUpdateClothingItem(item)}
          />

          <Button
            title="Delete"
            onPress={() => handleDeleteClothingItem(item.id)}
          />
        </View>
      ))}

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
        title="Load Wardrobe"
        onPress={testWardrobe}
      />

      <Button
        title="Create Test Item"
        onPress={testCreateClothingItem}
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
