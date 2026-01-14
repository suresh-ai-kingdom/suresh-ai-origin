"""Android Client Starter Template - Kotlin Compose"""

android_starter = """
// MainActivity.kt - Main app entry point

package com.sureshai.origin

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.navigation.NavDestination.Companion.hierarchy
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import androidx.work.OneTimeWorkRequestBuilder
import androidx.work.WorkManager
import com.sureshai.sdk.SureshAIClient
import kotlinx.coroutines.launch

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        
        setContent {
            SureshAITheme {
                val navController = rememberNavController()
                val viewModel = SureshAIViewModel()
                
                Scaffold(
                    bottomBar = {
                        NavigationBar {
                            val navBackStackEntry by navController.currentBackStackEntryAsState()
                            val currentDestination = navBackStackEntry?.destination
                            
                            NavigationBarItem(
                                icon = { Icon(Icons.Default.Edit, contentDescription = "Generate") },
                                label = { Text("Generate") },
                                selected = currentDestination?.hierarchy?.any { 
                                    it.route == "generate" 
                                } == true,
                                onClick = { navController.navigate("generate") }
                            )
                            
                            NavigationBarItem(
                                icon = { Icon(Icons.Default.LibraryBooks, contentDescription = "Library") },
                                label = { Text("Library") },
                                selected = currentDestination?.hierarchy?.any { 
                                    it.route == "library" 
                                } == true,
                                onClick = { navController.navigate("library") }
                            )
                            
                            NavigationBarItem(
                                icon = { Icon(Icons.Default.BarChart, contentDescription = "Analytics") },
                                label = { Text("Analytics") },
                                selected = currentDestination?.hierarchy?.any { 
                                    it.route == "analytics" 
                                } == true,
                                onClick = { navController.navigate("analytics") }
                            )
                            
                            NavigationBarItem(
                                icon = { Icon(Icons.Default.Settings, contentDescription = "Settings") },
                                label = { Text("Settings") },
                                selected = currentDestination?.hierarchy?.any { 
                                    it.route == "settings" 
                                } == true,
                                onClick = { navController.navigate("settings") }
                            )
                        }
                    }
                ) { paddingValues ->
                    NavHost(
                        navController = navController,
                        startDestination = "login",
                        modifier = Modifier.padding(paddingValues)
                    ) {
                        composable("login") {
                            LoginScreen(viewModel) { 
                                navController.navigate("generate") {
                                    popUpTo("login") { inclusive = true }
                                }
                            }
                        }
                        
                        composable("generate") {
                            GenerateScreen(viewModel)
                        }
                        
                        composable("library") {
                            LibraryScreen(viewModel)
                        }
                        
                        composable("analytics") {
                            AnalyticsScreen(viewModel)
                        }
                        
                        composable("settings") {
                            SettingsScreen(viewModel)
                        }
                    }
                }
            }
        }
    }
}

// MARK: - Login Screen

@Composable
fun LoginScreen(
    viewModel: SureshAIViewModel,
    onLoginSuccess: () -> Unit
) {
    val email = remember { mutableStateOf("") }
    val password = remember { mutableStateOf("") }
    val isLoading = remember { mutableStateOf(false) }
    val errorMessage = remember { mutableStateOf("") }
    val scope = rememberCoroutineScope()
    
    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(
                brush = Brush.linearGradient(
                    colors = listOf(
                        Color(0xfff55a4a),
                        Color(0xffff9f5e)
                    )
                )
            ),
        contentAlignment = Alignment.Center
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth(0.9f)
                .background(Color.White, RoundedCornerShape(12.dp))
                .padding(24.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.Center
        ) {
            Icon(
                imageVector = Icons.Default.Psychology,
                contentDescription = null,
                modifier = Modifier.size(48.dp),
                tint = Color(0xfff55a4a)
            )
            
            Spacer(modifier = Modifier.height(16.dp))
            
            Text(
                "SURESH AI",
                fontSize = 24.sp,
                fontWeight = androidx.compose.ui.text.font.FontWeight.Bold
            )
            
            Spacer(modifier = Modifier.height(32.dp))
            
            OutlinedTextField(
                value = email.value,
                onValueChange = { email.value = it },
                label = { Text("Email") },
                modifier = Modifier.fillMaxWidth()
            )
            
            Spacer(modifier = Modifier.height(12.dp))
            
            OutlinedTextField(
                value = password.value,
                onValueChange = { password.value = it },
                label = { Text("Password") },
                modifier = Modifier.fillMaxWidth(),
                visualTransformation = PasswordVisualTransformation()
            )
            
            if (errorMessage.value.isNotEmpty()) {
                Spacer(modifier = Modifier.height(8.dp))
                Text(
                    errorMessage.value,
                    color = Color.Red,
                    fontSize = 12.sp
                )
            }
            
            Spacer(modifier = Modifier.height(24.dp))
            
            Button(
                onClick = {
                    isLoading.value = true
                    scope.launch {
                        try {
                            viewModel.login(email.value, password.value)
                            onLoginSuccess()
                        } catch (e: Exception) {
                            errorMessage.value = e.message ?: "Login failed"
                        } finally {
                            isLoading.value = false
                        }
                    }
                },
                modifier = Modifier.fillMaxWidth(),
                enabled = !isLoading.value
            ) {
                if (isLoading.value) {
                    CircularProgressIndicator(
                        modifier = Modifier.size(20.dp),
                        color = Color.White
                    )
                } else {
                    Text("Sign In")
                }
            }
        }
    }
}

// MARK: - Generate Screen

@Composable
fun GenerateScreen(viewModel: SureshAIViewModel) {
    val prompt = remember { mutableStateOf("") }
    val selectedTemplate = remember { mutableStateOf("blog_post") }
    val isGenerating = remember { mutableStateOf(false) }
    val generatedContent = remember { mutableStateOf("") }
    val scope = rememberCoroutineScope()
    
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp)
    ) {
        Text(
            "What would you like to create?",
            style = MaterialTheme.typography.headlineSmall
        )
        
        Spacer(modifier = Modifier.height(12.dp))
        
        OutlinedTextField(
            value = prompt.value,
            onValueChange = { prompt.value = it },
            modifier = Modifier
                .fillMaxWidth()
                .height(120.dp),
            label = { Text("Enter prompt") },
            maxLines = 5
        )
        
        Spacer(modifier = Modifier.height(12.dp))
        
        DropdownMenu(
            modifier = Modifier.fillMaxWidth(),
            label = "Template",
            options = listOf("blog_post", "email", "product_description", "social_media"),
            selectedOption = selectedTemplate.value,
            onOptionSelected = { selectedTemplate.value = it }
        )
        
        Spacer(modifier = Modifier.height(16.dp))
        
        Button(
            onClick = {
                isGenerating.value = true
                scope.launch {
                    try {
                        val result = viewModel.generateContent(
                            prompt.value,
                            selectedTemplate.value
                        )
                        generatedContent.value = result
                    } catch (e: Exception) {
                        generatedContent.value = "Error: \${e.message}"
                    } finally {
                        isGenerating.value = false
                    }
                }
            },
            modifier = Modifier.fillMaxWidth(),
            enabled = prompt.value.isNotEmpty() && !isGenerating.value
        ) {
            if (isGenerating.value) {
                CircularProgressIndicator(modifier = Modifier.size(20.dp))
            } else {
                Text("Generate Content")
            }
        }
        
        if (generatedContent.value.isNotEmpty()) {
            Spacer(modifier = Modifier.height(16.dp))
            
            Card(
                modifier = Modifier.fillMaxWidth(),
                colors = CardDefaults.cardColors(containerColor = Color(0xfff5f5f5))
            ) {
                Column(
                    modifier = Modifier.padding(12.dp)
                ) {
                    Text(
                        "Generated Content",
                        style = MaterialTheme.typography.labelLarge
                    )
                    
                    Spacer(modifier = Modifier.height(8.dp))
                    
                    Text(generatedContent.value)
                    
                    Spacer(modifier = Modifier.height(12.dp))
                    
                    Button(
                        onClick = { viewModel.saveContent(generatedContent.value) },
                        modifier = Modifier.fillMaxWidth()
                    ) {
                        Text("Save to Library")
                    }
                }
            }
        }
    }
}

// MARK: - ViewModel

class SureshAIViewModel : ViewModel() {
    private val client = SureshAIClient(apiVersion = "v2")
    private val offlineDB = OfflineDatabase()
    
    suspend fun login(email: String, password: String) {
        val token = client.auth.login(email, password)
        offlineDB.saveToken(token)
    }
    
    suspend fun generateContent(prompt: String, template: String): String {
        val response = client.content.generate(prompt, template)
        offlineDB.saveContent(response)
        return response
    }
    
    fun saveContent(content: String) {
        // Save to local database
    }
}

// MARK: - Theme

@Composable
fun SureshAITheme(content: @Composable () -> Unit) {
    MaterialTheme(
        colorScheme = lightColorScheme(
            primary = Color(0xfff55a4a),
            secondary = Color(0xffff9f5e),
            tertiary = Color(0xff4facfe)
        ),
        content = content
    )
}

// build.gradle.kts

dependencies {
    implementation("androidx.compose.ui:ui")
    implementation("androidx.compose.material3:material3")
    implementation("androidx.activity:activity-compose:1.8.0")
    implementation("androidx.navigation:navigation-compose:2.7.0")
    implementation("androidx.lifecycle:lifecycle-viewmodel-compose:2.6.1")
    implementation("com.sureshai:sdk:2.0.0")
    implementation("androidx.work:work-runtime-ktx:2.8.1")
}
"""

print("Android Kotlin Compose starter template created")
print("Setup: Create Android Studio project, add SureshAI Gradle dependency")
