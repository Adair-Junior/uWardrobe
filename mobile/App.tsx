import { useEffect, useState } from 'react';
import { StatusBar } from 'expo-status-bar';
import { Button, StyleSheet, Text, TextInput, ScrollView, View } from 'react-native';

import { 
  ClothingItem,
  createClothingItem,
  createStyleProfile,
  deleteClothingItem,
  getCurrentUser, 
  getHealth,
  getStyleProfile,
  updateStyleProfile,
  getWardrobe,
  loginUser, 
  registerUser,
  StyleProfile,
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

  const [styleProfile, setStyleProfile] = useState<StyleProfile | null>(null);

  const [profileStatus, setProfileStatus] = useState(
    'Profile not loaded'
  );

  const [preferredStylesInput, setPreferredStylesInput] = useState('');

  const [preferredColorsInput, setPreferredColorsInput] = useState('');

  const [avoidedColorsInput, setAvoidedColorsInput] = useState('');

  const [topSizeInput, setTopSizeInput] = useState('');

  const [bottomSizeInput, setBottomSizeInput] = useState('');

  const [shoeSizeInput, setShoeSizeInput] = useState('');

  const [preferredFitInput, setPreferredFitInput] = useState('');

  const [preferredOccasionsInput, setPreferredOccasionsInput] = useState('');

  const [temperaturePreferenceInput, setTemperaturePreferenceInput] =
  useState('');

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

  const testStyleProfile = async () => {
    if (!accessToken) {
      setProfileStatus('Please log in first');
      return;
    }

    try {
      const profile = await getStyleProfile(accessToken);

      setStyleProfile(profile);

      setPreferredStylesInput(profile.preferred_styles.join(', '));
      setPreferredColorsInput(profile.preferred_colors.join(', '));
      setAvoidedColorsInput(profile.avoided_colors.join(', '));
      setTopSizeInput(profile.top_size ?? '');
      setBottomSizeInput(profile.bottom_size ?? '');
      setShoeSizeInput(profile.shoe_size ?? '');
      setPreferredFitInput(profile.preferred_fit ?? '');
      setPreferredOccasionsInput(profile.preferred_occasions.join(', '));
      setTemperaturePreferenceInput(profile.temperature_preference ?? '');

      console.log('Style profile:', profile);
      setProfileStatus('Profile loaded successfully');
    } catch (error) {
      console.error('Profile load failed:', error);
      setProfileStatus(`Profile load failed: ${String(error)}`);
    }
  };

  const testCreateStyleProfile = async () => {
    if (!accessToken) {
      setProfileStatus('Please log in first');
      return;
    }

    try {
      const profile = await createStyleProfile(accessToken, {
        preferred_styles: ['casual', 'minimalist'],
        preferred_colors: ['black', 'white'],
        avoided_colors: ['neon'],
        top_size: 'M',
        bottom_size: 'M',
        shoe_size: '42',
        preferred_fit: 'regular',
        preferred_occasions: ['casual', 'work'],
        temperature_preference: 'neutral',
      });

      setStyleProfile(profile);
      console.log('Created style profile:', profile);
      setProfileStatus('Profile created successfully');
    } catch (error) {
      console.error('Profile creation failed:', error);
      setProfileStatus(`Profile creation failed: ${String(error)}`);
    }
  };

  const testUpdateStyleProfile = async () => {
    if (!accessToken) {
      setProfileStatus('Please log in first');
      return;
    }

    try {
      const profile = await updateStyleProfile(accessToken, {
        preferred_styles: preferredStylesInput
          .split(',')
          .map((value) => value.trim())
          .filter(Boolean),
        preferred_colors: preferredColorsInput
          .split(',')
          .map((value) => value.trim())
          .filter(Boolean),
        avoided_colors: avoidedColorsInput
          .split(',')
          .map((value) => value.trim())
          .filter(Boolean),
        top_size: topSizeInput.trim() || null,
        bottom_size: bottomSizeInput.trim() || null,
        shoe_size: shoeSizeInput.trim() || null,
        preferred_fit: preferredFitInput.trim() || null,
        preferred_occasions: preferredOccasionsInput
          .split(',')
          .map((value) => value.trim())
          .filter(Boolean),
        temperature_preference:
          temperaturePreferenceInput.trim() || null,
      });

      setStyleProfile(profile);
      console.log('Updated style profile:', profile);
      setProfileStatus('Profile updated successfully');
    } catch (error) {
      console.error('Profile update failed:', error);
      setProfileStatus(`Profile update failed: ${String(error)}`);
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
    <ScrollView contentContainerStyle={styles.container}>
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

      <Text>Preferred Styles</Text>

      <TextInput
        value={preferredStylesInput}
        onChangeText={setPreferredStylesInput}
        placeholder="casual, minimalist"
        autoCapitalize="none"
        style={styles.profileInput}
      />

      <Text>Preferred Colors</Text>

      <TextInput
        value={preferredColorsInput}
        onChangeText={setPreferredColorsInput}
        placeholder="black, white, blue"
        autoCapitalize="none"
        style={styles.profileInput}
      />

      <Text>Avoided Colors</Text>

      <TextInput
        value={avoidedColorsInput}
        onChangeText={setAvoidedColorsInput}
        placeholder="orange, neon"
        autoCapitalize="none"
        style={styles.profileInput}
      />

      <Text>Top Size</Text>

      <TextInput
        value={topSizeInput}
        onChangeText={setTopSizeInput}
        placeholder="M"
        autoCapitalize="characters"
        style={styles.profileInput}
      />

      <Text>Bottom Size</Text>

      <TextInput
        value={bottomSizeInput}
        onChangeText={setBottomSizeInput}
        placeholder="M"
        autoCapitalize="characters"
        style={styles.profileInput}
      />

      <Text>Shoe Size</Text>

      <TextInput
        value={shoeSizeInput}
        onChangeText={setShoeSizeInput}
        placeholder="42"
        keyboardType="default"
        style={styles.profileInput}
      />

      <Text>Preferred Fit</Text>

      <TextInput
        value={preferredFitInput}
        onChangeText={setPreferredFitInput}
        placeholder="regular, relaxed, slim"
        autoCapitalize="none"
        style={styles.profileInput}
      />

      <Text>Preferred Occasions</Text>

      <TextInput
        value={preferredOccasionsInput}
        onChangeText={setPreferredOccasionsInput}
        placeholder="casual, work, weekend"
        autoCapitalize="none"
        style={styles.profileInput}
      />

      <Text>Temperature Preference</Text>

      <TextInput
        value={temperaturePreferenceInput}
        onChangeText={setTemperaturePreferenceInput}
        placeholder="cold_sensitive, neutral, heat_sensitive"
        autoCapitalize="none"
        style={styles.profileInput}
      />

      <Text>{profileStatus}</Text>

      {styleProfile && (
        <View>
          <Text>Styles: {styleProfile.preferred_styles.join(', ')}</Text>
          <Text>Colors: {styleProfile.preferred_colors.join(', ')}</Text>
          <Text>Avoided colors: {styleProfile.avoided_colors.join(', ')}</Text>
          <Text>Top size: {styleProfile.top_size || 'Not set'}</Text>
          <Text>Bottom size: {styleProfile.bottom_size || 'Not set'}</Text>
          <Text>Shoe size: {styleProfile.shoe_size || 'Not set'}</Text>
          <Text>Fit: {styleProfile.preferred_fit || 'Not set'}</Text>
          <Text>
            Occasions: {styleProfile.preferred_occasions.join(', ')}
          </Text>
          <Text>
            Temperature: {styleProfile.temperature_preference || 'Not set'}
          </Text>
        </View>
      )}

      <Button
        title="Load Profile"
        onPress={testStyleProfile}
      />

      <Button
        title="Create Profile"
        onPress={testCreateStyleProfile}
      />

      <Button
        title="Update Profile"
        onPress={testUpdateStyleProfile}
      />

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
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
    alignItems: 'center',
    justifyContent: 'center',
  },

    profileInput: {
    borderWidth: 1,
    padding: 10,
    width: 250,
    marginBottom: 10,
  },

});
