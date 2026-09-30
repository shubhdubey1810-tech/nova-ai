package com.example.novaai

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import java.net.HttpURLConnection
import java.net.URL

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        setContent {
            NovaAIApp()
        }
    }
}

@Composable
fun NovaAIApp() {
    var message by remember { mutableStateOf("") }
    var response by remember { mutableStateOf("Hello! I am Nova AI.") }
    var loading by remember { mutableStateOf(false) }
    val coroutineScope = rememberCoroutineScope()

    MaterialTheme {
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(20.dp)
        ) {

            Text(
                text = "NØVA AI",
                style = MaterialTheme.typography.headlineLarge
            )

            Spacer(modifier = Modifier.height(20.dp))

            Text(
                text = response,
                style = MaterialTheme.typography.bodyLarge
            )

            Spacer(modifier = Modifier.height(20.dp))

            OutlinedTextField(
                value = message,
                onValueChange = { message = it },
                modifier = Modifier.fillMaxWidth(),
                label = { Text("Ask Nova AI") }
            )

            Spacer(modifier = Modifier.height(12.dp))

            Button(
                onClick = {
                    loading = true
                    response = "Connecting to Nova AI..."

                    coroutineScope.launch {
                        withContext(Dispatchers.IO) {
                            try {
                                val url = URL("http://10.0.2.2:8000/")
                                val connection = (url.openConnection() as HttpURLConnection).apply {
                                    requestMethod = "GET"
                                    connectTimeout = 5000
                                    readTimeout = 5000
                                }

                                val result = connection.responseCode
                                val responseText = if (result == 200) {
                                    connection.inputStream.bufferedReader().use { it.readText() }
                                } else {
                                    ""
                                }

                                withContext(Dispatchers.Main) {
                                    response = if (result == 200) {
                                        if (responseText.isNotBlank()) "✅ Connected: $responseText" else "✅ Nova AI Backend Connected!"
                                    } else {
                                        "❌ Backend returned HTTP $result"
                                    }
                                    loading = false
                                }

                                connection.disconnect()

                            } catch (e: Exception) {
                                val errorMsg = e.localizedMessage ?: e.toString()
                                withContext(Dispatchers.Main) {
                                    response = "❌ Connection failed: $errorMsg"
                                    loading = false
                                }
                            }
                        }
                    }
                },
                modifier = Modifier.fillMaxWidth()
            ) {
                Text(if (loading) "Connecting..." else "Test Nova AI")
            }
        }
    }
}