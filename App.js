import React, { useState } from "react";
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  Alert,
} from "react-native";

export default function App() {
  const [videoName, setVideoName] = useState("");

  const selectVideo = () => {
    Alert.alert(
      "Movie Recap",
      "Video picker ကို နောက်အဆင့်မှာ ထည့်ပေးမယ် 😁"
    );
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>🎬 Movie Recap</Text>

      <Text style={styles.subtitle}>
        AI နဲ့ Movie Recap ပြုလုပ်မယ်
      </Text>

      <TouchableOpacity
        style={styles.button}
        onPress={selectVideo}
      >
        <Text style={styles.buttonText}>🎥 Select Video</Text>
      </TouchableOpacity>

      {videoName !== "" && (
        <Text style={styles.videoName}>
          Selected: {videoName}
        </Text>
      )}

      <Text style={styles.result}>
        Your movie recap will appear here.
      </Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 25,
    justifyContent: "center",
  },

  title: {
    fontSize: 32,
    fontWeight: "bold",
    textAlign: "center",
    marginBottom: 10,
  },

  subtitle: {
    fontSize: 16,
    textAlign: "center",
    marginBottom: 40,
  },

  button: {
    padding: 18,
    borderRadius: 12,
    backgroundColor: "#222",
    alignItems: "center",
  },

  buttonText: {
    color: "white",
    fontSize: 18,
    fontWeight: "bold",
  },

  videoName: {
    marginTop: 20,
    fontSize: 15,
  },

  result: {
    marginTop: 40,
    fontSize: 16,
    textAlign: "center",
  },
});
