package com.example.novaai

import android.Manifest
import android.content.Intent
import android.content.pm.PackageManager
import android.os.Bundle
import android.speech.RecognitionListener
import android.speech.RecognizerIntent
import android.speech.SpeechRecognizer
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.credentials.CredentialManager
import androidx.credentials.CustomCredential
import androidx.credentials.GetCredentialRequest
import com.google.android.libraries.identity.googleid.GetGoogleIdOption
import com.google.android.libraries.identity.googleid.GoogleIdTokenCredential
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import org.json.JSONObject
import java.net.HttpURLConnection
import java.net.URL
import java.util.UUID

class MainActivity : ComponentActivity() {

    private var speechRecognizer: SpeechRecognizer? = null

    private val microphonePermission =
        registerForActivityResult(
            ActivityResultContracts.RequestPermission()
        ) { granted ->
            if (granted) {
                startVoiceRecognition()
            }
        }

    private var onSpeechResult: ((String) -> Unit)? = null

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        setContent {
            NovaAIApp(
                onMicrophoneClick = { onResult ->
                    onSpeechResult = onResult

                    if (
                        checkSelfPermission(
                            Manifest.permission.RECORD_AUDIO
                        ) == PackageManager.PERMISSION_GRANTED
                    ) {
                        startVoiceRecognition()
                    } else {
                        microphonePermission.launch(
                            Manifest.permission.RECORD_AUDIO
                        )
                    }
                }
            )
        }
    }

    private fun startVoiceRecognition() {

        if (!SpeechRecognizer.isRecognitionAvailable(this)) {
            onSpeechResult?.invoke(
                "Voice recognition is not available on this device."
            )
            return
        }

        speechRecognizer?.destroy()

        speechRecognizer = SpeechRecognizer.createSpeechRecognizer(this)

        speechRecognizer?.setRecognitionListener(
            object : RecognitionListener {

                override fun onReadyForSpeech(params: Bundle?) {}

                override fun onBeginningOfSpeech() {}

                override fun onRmsChanged(rmsdB: Float) {}

                override fun onBufferReceived(buffer: ByteArray?) {}

                override fun onEndOfSpeech() {}

                override fun onPartialResults(
                    partialResults: Bundle?
                ) {}

                override fun onEvent(
                    eventType: Int,
                    params: Bundle?
                ) {}

                override fun onError(error: Int) {
                    onSpeechResult?.invoke("")
                }

                override fun onResults(results: Bundle?) {

                    val matches =
                        results?.getStringArrayList(
                            SpeechRecognizer.RESULTS_RECOGNITION
                        )

                    val text =
                        matches?.firstOrNull() ?: ""

                    onSpeechResult?.invoke(text)
                }
            }
        )

        val intent = Intent(
            RecognizerIntent.ACTION_RECOGNIZE_SPEECH
        ).apply {

            putExtra(
                RecognizerIntent.EXTRA_LANGUAGE_MODEL,
                RecognizerIntent.LANGUAGE_MODEL_FREE_FORM
            )

            putExtra(
                RecognizerIntent.EXTRA_LANGUAGE,
                java.util.Locale.getDefault()
            )

            putExtra(
                RecognizerIntent.EXTRA_PARTIAL_RESULTS,
                true
            )
        }

        speechRecognizer?.startListening(intent)
    }

    override fun onDestroy() {
        speechRecognizer?.destroy()
        speechRecognizer = null
        super.onDestroy()
    }
}


data class ChatMessage(
    val text: String,
    val isUser: Boolean
)


@Composable
fun NovaAIApp(
    onMicrophoneClick: ((String) -> Unit) -> Unit
) {

    var message by remember {
        mutableStateOf("")
    }

    var loading by remember {
        mutableStateOf(false)
    }

    var isListening by remember {
        mutableStateOf(false)
    }

    var showMemory by remember {
        mutableStateOf(false)
    }

    var showTools by remember {
        mutableStateOf(false)
    }

    val messages = remember {
        mutableStateListOf<ChatMessage>()
    }

    val coroutineScope = rememberCoroutineScope()

    val context = LocalContext.current

    val credentialManager = remember(context) {
        CredentialManager.create(context)
    }

    var googleEmail by remember {
        mutableStateOf<String?>(null)
    }

    var googleName by remember {
        mutableStateOf<String?>(null)
    }

    MaterialTheme(
        colorScheme = darkColorScheme(
            background = Color(0xFF0A0A0A),
            surface = Color(0xFF111111),
            primary = Color.White,
            onPrimary = Color.Black,
            onBackground = Color.White,
            onSurface = Color.White
        )
    ) {

        Column(
            modifier = Modifier
                .fillMaxSize()
                .background(Color(0xFF0A0A0A))
        ) {

            // TOP BAR

            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(
                        horizontal = 18.dp,
                        vertical = 16.dp
                    ),
                verticalAlignment = Alignment.CenterVertically
            ) {

                Column(
                    modifier = Modifier.weight(1f)
                ) {

                    Text(
                        text = "NØVA AI",
                        fontSize = 20.sp,
                        fontWeight = FontWeight.Bold
                    )

                    Text(
                        text = "● Online",
                        color = Color(0xFF7CFF8B),
                        fontSize = 12.sp
                    )
                }

                OutlinedButton(
                    onClick = {

                        coroutineScope.launch {

                            try {

                                val googleIdOption =
                                    GetGoogleIdOption.Builder()
                                        .setFilterByAuthorizedAccounts(false)
                                        .setServerClientId(
                                            "670068485437-j90jpjjtu83o5tlsqpae4vr7fgbnvpc3.apps.googleusercontent.com"
                                        )
                                        .setAutoSelectEnabled(false)
                                        .build()

                                val request =
                                    GetCredentialRequest.Builder()
                                        .addCredentialOption(
                                            googleIdOption
                                        )
                                        .build()

                                val result =
                                    credentialManager.getCredential(
                                        context = context,
                                        request = request
                                    )

                                val credential =
                                    result.credential

                                if (
                                    credential is CustomCredential &&
                                    credential.type ==
                                    GoogleIdTokenCredential
                                        .TYPE_GOOGLE_ID_TOKEN_CREDENTIAL
                                ) {

                                    val googleCredential =
                                        GoogleIdTokenCredential
                                            .createFrom(
                                                credential.data
                                            )

                                    googleName =
                                        googleCredential.displayName

                                    googleEmail =
                                        googleCredential.id

                                }

                            } catch (e: Exception) {

                                googleName = "Google Sign-In failed"

                                googleEmail =
                                    "${e::class.java.simpleName}: " +
                                    "${e.localizedMessage ?: "Unknown error"}"
                            }
                        }
                    },
                    shape = RoundedCornerShape(10.dp)
                ) {
                    Text(
                        text =
                            googleName
                                ?: "Continue with Google"
                    )
                }
            }


            HorizontalDivider(
                color = Color(0xFF252525)
            )


            // SEARCH BAR

            OutlinedTextField(
                value = "",
                onValueChange = {},
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(
                        horizontal = 16.dp,
                        vertical = 12.dp
                    ),
                placeholder = {
                    Text(
                        "Search the web or ask NØVA..."
                    )
                },
                singleLine = true,
                shape = RoundedCornerShape(14.dp),
                colors = OutlinedTextFieldDefaults.colors(
                    focusedBorderColor = Color(0xFF555555),
                    unfocusedBorderColor = Color(0xFF303030),
                    focusedContainerColor = Color(0xFF151515),
                    unfocusedContainerColor = Color(0xFF151515)
                )
            )


            // QUICK ACTIONS

            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(
                        horizontal = 16.dp
                    ),
                horizontalArrangement =
                    Arrangement.spacedBy(8.dp)
            ) {

                Button(
                    onClick = {
                        messages.clear()
                        message = ""
                    },
                    modifier = Modifier.weight(1f)
                ) {
                    Text("+ New Chat")
                }

                OutlinedButton(
                    onClick = {
                        showMemory = true
                    },
                    modifier = Modifier.weight(1f)
                ) {
                    Text("Memory")
                }

                OutlinedButton(
                    onClick = {
                        showTools = true
                    },
                    modifier = Modifier.weight(1f)
                ) {
                    Text("Tools")
                }
            }


            // CHAT AREA

            Box(
                modifier = Modifier
                    .weight(1f)
                    .fillMaxWidth()
            ) {

                if (messages.isEmpty()) {

                    Column(
                        modifier = Modifier
                            .fillMaxSize()
                            .padding(25.dp),
                        horizontalAlignment =
                            Alignment.CenterHorizontally,
                        verticalArrangement =
                            Arrangement.Center
                    ) {

                        Text(
                            text = "NØVA",
                            fontSize = 48.sp,
                            fontWeight = FontWeight.Bold
                        )

                        Spacer(
                            modifier =
                                Modifier.height(18.dp)
                        )

                        Text(
                            text =
                                "What can I help you with?",
                            fontSize = 27.sp,
                            fontWeight =
                                FontWeight.SemiBold
                        )

                        Spacer(
                            modifier =
                                Modifier.height(8.dp)
                        )

                        Text(
                            text = "Ask NØVA anything.",
                            color =
                                Color(0xFF888888)
                        )
                    }

                } else {

                    LazyColumn(
                        modifier = Modifier
                            .fillMaxSize()
                            .padding(
                                horizontal = 16.dp
                            ),
                        reverseLayout = false
                    ) {

                        items(messages) { item ->

                            MessageBubble(
                                message = item
                            )

                            Spacer(
                                modifier =
                                    Modifier.height(12.dp)
                            )
                        }

                        if (loading) {

                            item {

                                Text(
                                    text =
                                        "NØVA is thinking...",
                                    color =
                                        Color(0xFF888888),
                                    modifier =
                                        Modifier.padding(
                                            12.dp
                                        )
                                )
                            }
                        }
                    }
                }
            }


            // INPUT AREA

            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(
                        horizontal = 12.dp,
                        vertical = 12.dp
                    ),
                verticalAlignment =
                    Alignment.CenterVertically
            ) {

                OutlinedTextField(
                    value = message,
                    onValueChange = {
                        message = it
                    },
                    modifier = Modifier.weight(1f),
                    placeholder = {
                        Text("Message NØVA...")
                    },
                    enabled = !loading,
                    maxLines = 4,
                    shape = RoundedCornerShape(16.dp),
                    colors =
                        OutlinedTextFieldDefaults.colors(
                            focusedBorderColor =
                                Color(0xFF555555),
                            unfocusedBorderColor =
                                Color(0xFF303030),
                            focusedContainerColor =
                                Color(0xFF151515),
                            unfocusedContainerColor =
                                Color(0xFF151515)
                        )
                )


                Spacer(
                    modifier =
                        Modifier.width(7.dp)
                )


                // MICROPHONE

                Button(
                    onClick = {

                        isListening = true

                        onMicrophoneClick { spokenText ->

                            if (spokenText.isNotBlank()) {
                                message = spokenText
                            }

                            isListening = false
                        }
                    },
                    modifier = Modifier.size(52.dp),
                    contentPadding =
                        PaddingValues(0.dp),
                    shape =
                        RoundedCornerShape(14.dp),
                    colors =
                        ButtonDefaults.buttonColors(
                            containerColor =
                                if (isListening)
                                    Color(0xFF444444)
                                else
                                    Color.White,
                            contentColor =
                                Color.Black
                        )
                ) {

                    Text(
                        text =
                            if (isListening)
                                "●"
                            else
                                "🎤",
                        fontSize = 19.sp
                    )
                }


                Spacer(
                    modifier =
                        Modifier.width(7.dp)
                )


                // SEND

                Button(
                    onClick = {

                        if (
                            message.isBlank() ||
                            loading
                        ) {
                            return@Button
                        }

                        val question =
                            message.trim()

                        messages.add(
                            ChatMessage(
                                text = question,
                                isUser = true
                            )
                        )

                        message = ""
                        loading = true

                        coroutineScope.launch {

                            val result =
                                askNovaAI(question)

                            messages.add(
                                ChatMessage(
                                    text = result,
                                    isUser = false
                                )
                            )

                            loading = false
                        }
                    },
                    modifier = Modifier.size(52.dp),
                    contentPadding =
                        PaddingValues(0.dp),
                    shape =
                        RoundedCornerShape(14.dp),
                    enabled = !loading
                ) {

                    Text(
                        text = "↑",
                        fontSize = 22.sp
                    )
                }
            }
        }


        // MEMORY DIALOG

        if (showMemory) {

            AlertDialog(
                onDismissRequest = {
                    showMemory = false
                },
                title = {
                    Text("NØVA Memory")
                },
                text = {
                    Text(
                        "Memory management will be connected to the Nova AI backend."
                    )
                },
                confirmButton = {
                    TextButton(
                        onClick = {
                            showMemory = false
                        }
                    ) {
                        Text("Close")
                    }
                }
            )
        }


        // TOOLS DIALOG

        if (showTools) {

            AlertDialog(
                onDismissRequest = {
                    showTools = false
                },
                title = {
                    Text("NØVA Tools")
                },
                text = {
                    Text(
                        "Tools will be connected to the Nova AI backend."
                    )
                },
                confirmButton = {
                    TextButton(
                        onClick = {
                            showTools = false
                        }
                    ) {
                        Text("Close")
                    }
                }
            )
        }
    }
}


@Composable
fun MessageBubble(
    message: ChatMessage
) {

    Row(
        modifier = Modifier.fillMaxWidth(),
        horizontalArrangement =
            if (message.isUser)
                Arrangement.End
            else
                Arrangement.Start
    ) {

        Surface(
            color =
                if (message.isUser)
                    Color(0xFF222222)
                else
                    Color(0xFF141414),
            shape =
                RoundedCornerShape(14.dp),
            border =
                if (!message.isUser)
                    androidx.compose.foundation.BorderStroke(
                        1.dp,
                        Color(0xFF252525)
                    )
                else
                    null
        ) {

            Text(
                text = message.text,
                modifier = Modifier.padding(
                    horizontal = 16.dp,
                    vertical = 13.dp
                ),
                color = Color.White,
                fontSize = 15.sp
            )
        }
    }
}


private const val BASE_URL =
    "http://10.158.193.190:8000"


private suspend fun askNovaAI(
    question: String
): String {

    return withContext(Dispatchers.IO) {

        var connection:
                HttpURLConnection? = null

        try {

            val url =
                URL("$BASE_URL/chat")

            connection =
                url.openConnection()
                        as HttpURLConnection

            connection.requestMethod = "POST"

            connection.connectTimeout = 10000

            connection.readTimeout = 60000

            connection.doInput = true

            connection.doOutput = true

            connection.setRequestProperty(
                "Content-Type",
                "application/json"
            )

            connection.setRequestProperty(
                "Accept",
                "application/json"
            )

            val json =
                JSONObject().apply {

                    put(
                        "conversation_id",
                        "android-${UUID.randomUUID()}"
                    )

                    put(
                        "message",
                        question
                    )
                }

            connection.outputStream.use { output ->

                output.write(
                    json.toString()
                        .toByteArray(
                            Charsets.UTF_8
                        )
                )

                output.flush()
            }

            val statusCode =
                connection.responseCode

            val stream =
                if (statusCode in 200..299) {

                    connection.inputStream

                } else {

                    connection.errorStream
                }

            val body =
                stream
                    ?.bufferedReader()
                    ?.use { reader ->
                        reader.readText()
                    }
                    ?: ""

            if (statusCode !in 200..299) {

                return@withContext(
                        "❌ Backend error: HTTP $statusCode\n\n" +
                                if (body.isNotBlank()) {
                                    body
                                } else {
                                    "The Nova AI server returned an error."
                                }
                        )
            }

            if (body.isBlank()) {

                return@withContext(
                        "❌ Nova AI returned an empty response."
                        )
            }

            try {

                val jsonResponse =
                    JSONObject(body)

                val answer = when {

                    jsonResponse.has("response") ->
                        jsonResponse.optString(
                            "response"
                        )

                    jsonResponse.has("answer") ->
                        jsonResponse.optString(
                            "answer"
                        )

                    jsonResponse.has("message") ->
                        jsonResponse.optString(
                            "message"
                        )

                    jsonResponse.has("content") ->
                        jsonResponse.optString(
                            "content"
                        )

                    jsonResponse.has("text") ->
                        jsonResponse.optString(
                            "text"
                        )

                    else ->
                        body
                }

                if (answer.isNotBlank()) {
                    answer
                } else {
                    body
                }

            } catch (_: Exception) {

                body
            }

        } catch (e: Exception) {

            "❌ Connection failed:\n" +
                    "${e.localizedMessage ?: e}"

        } finally {

            connection?.disconnect()
        }
    }
}