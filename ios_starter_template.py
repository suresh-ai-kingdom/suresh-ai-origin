"""iOS Client Starter Template - SwiftUI"""

ios_starter = """
// ContentView.swift - Main app view

import SwiftUI
import SureshAI

struct ContentView: View {
    @StateObject var viewModel = AIViewModel()
    @State private var showingLogin = true
    
    var body: some View {
        if showingLogin {
            LoginView(viewModel: viewModel, showingLogin: $showingLogin)
        } else {
            MainTabView(viewModel: viewModel, showingLogin: $showingLogin)
        }
    }
}

// MARK: - Authentication

struct LoginView: View {
    @ObservedObject var viewModel: AIViewModel
    @Binding var showingLogin: Bool
    @State private var email = ""
    @State private var password = ""
    @State private var errorMessage = ""
    
    var body: some View {
        ZStack {
            LinearGradient(
                gradient: Gradient(colors: [
                    Color(red: 0.96, green: 0.36, blue: 0.45),
                    Color(red: 0.98, green: 0.60, blue: 0.50)
                ]),
                startPoint: .topLeading,
                endPoint: .bottomTrailing
            )
            .ignoresSafeArea()
            
            VStack(spacing: 20) {
                VStack(spacing: 10) {
                    Image(systemName: "brain.head.profile")
                        .font(.system(size: 48))
                        .foregroundColor(.white)
                    
                    Text("SURESH AI")
                        .font(.title)
                        .fontWeight(.bold)
                        .foregroundColor(.white)
                }
                .padding(.bottom, 40)
                
                VStack(spacing: 15) {
                    TextField("Email", text: $email)
                        .padding()
                        .background(Color.white.opacity(0.9))
                        .cornerRadius(8)
                    
                    SecureField("Password", text: $password)
                        .padding()
                        .background(Color.white.opacity(0.9))
                        .cornerRadius(8)
                    
                    if !errorMessage.isEmpty {
                        Text(errorMessage)
                            .foregroundColor(.red)
                            .font(.caption)
                    }
                    
                    Button(action: loginTapped) {
                        Text("Sign In")
                            .frame(maxWidth: .infinity)
                            .padding()
                            .background(Color.white)
                            .foregroundColor(Color(red: 0.96, green: 0.36, blue: 0.45))
                            .cornerRadius(8)
                            .fontWeight(.semibold)
                    }
                    
                    Button(action: signupTapped) {
                        Text("Create Account")
                            .frame(maxWidth: .infinity)
                            .padding()
                            .background(Color.white.opacity(0.3))
                            .foregroundColor(.white)
                            .cornerRadius(8)
                            .fontWeight(.semibold)
                    }
                }
                .padding(20)
                .background(Color.white.opacity(0.95))
                .cornerRadius(12)
                
                Spacer()
            }
            .padding()
        }
    }
    
    private func loginTapped() {
        Task {
            do {
                let token = try await viewModel.login(email: email, password: password)
                showingLogin = false
            } catch {
                errorMessage = error.localizedDescription
            }
        }
    }
    
    private func signupTapped() {
        // Navigate to signup
    }
}

// MARK: - Main App

struct MainTabView: View {
    @ObservedObject var viewModel: AIViewModel
    @Binding var showingLogin: Bool
    @State private var selectedTab = 0
    
    var body: some View {
        TabView(selection: $selectedTab) {
            // Content Generation Tab
            ContentGeneratorView(viewModel: viewModel)
                .tabItem {
                    Label("Generate", systemImage: "sparkles")
                }
                .tag(0)
            
            // Library Tab
            ContentLibraryView(viewModel: viewModel)
                .tabItem {
                    Label("Library", systemImage: "books.vertical")
                }
                .tag(1)
            
            // Analytics Tab
            AnalyticsView(viewModel: viewModel)
                .tabItem {
                    Label("Analytics", systemImage: "chart.bar")
                }
                .tag(2)
            
            // Settings Tab
            SettingsView(viewModel: viewModel, showingLogin: $showingLogin)
                .tabItem {
                    Label("Settings", systemImage: "gear")
                }
                .tag(3)
        }
    }
}

// MARK: - Content Generator

struct ContentGeneratorView: View {
    @ObservedObject var viewModel: AIViewModel
    @State private var prompt = ""
    @State private var selectedTemplate = "blog_post"
    @State private var isGenerating = false
    @State private var generatedContent = ""
    
    let templates = ["blog_post", "email", "product_description", "social_media"]
    
    var body: some View {
        NavigationView {
            VStack(spacing: 15) {
                VStack(alignment: .leading, spacing: 10) {
                    Text("What would you like to create?")
                        .font(.headline)
                    
                    TextEditor(text: $prompt)
                        .frame(height: 120)
                        .padding(8)
                        .background(Color.gray.opacity(0.1))
                        .cornerRadius(8)
                }
                .padding()
                
                VStack(alignment: .leading, spacing: 10) {
                    Text("Template")
                        .font(.headline)
                    
                    Picker("Template", selection: $selectedTemplate) {
                        ForEach(templates, id: \\.self) { template in
                            Text(template.replacingOccurrences(of: "_", with: " ")).tag(template)
                        }
                    }
                    .pickerStyle(.menu)
                    .padding(8)
                    .background(Color.gray.opacity(0.1))
                    .cornerRadius(8)
                }
                .padding()
                
                Button(action: generateContent) {
                    if isGenerating {
                        ProgressView()
                            .frame(maxWidth: .infinity)
                            .padding()
                    } else {
                        Text("Generate Content")
                            .frame(maxWidth: .infinity)
                            .padding()
                            .background(Color(red: 0.96, green: 0.36, blue: 0.45))
                            .foregroundColor(.white)
                            .cornerRadius(8)
                    }
                }
                .disabled(isGenerating || prompt.isEmpty)
                .padding()
                
                if !generatedContent.isEmpty {
                    VStack(alignment: .leading, spacing: 10) {
                        Text("Generated Content")
                            .font(.headline)
                        
                        ScrollView {
                            Text(generatedContent)
                                .padding()
                                .background(Color.gray.opacity(0.1))
                                .cornerRadius(8)
                        }
                        
                        HStack {
                            Button(action: { UIPasteboard.general.string = generatedContent }) {
                                Label("Copy", systemImage: "doc.on.doc")
                            }
                            .frame(maxWidth: .infinity)
                            .padding()
                            .background(Color.blue)
                            .foregroundColor(.white)
                            .cornerRadius(8)
                            
                            Button(action: saveContent) {
                                Label("Save", systemImage: "square.and.arrow.down")
                            }
                            .frame(maxWidth: .infinity)
                            .padding()
                            .background(Color.green)
                            .foregroundColor(.white)
                            .cornerRadius(8)
                        }
                    }
                    .padding()
                }
                
                Spacer()
            }
            .navigationTitle("AI Generator")
        }
    }
    
    private func generateContent() {
        isGenerating = true
        Task {
            do {
                let result = try await viewModel.generateContent(
                    prompt: prompt,
                    template: selectedTemplate
                )
                generatedContent = result
            } catch {
                generatedContent = "Error: \\(error.localizedDescription)"
            }
            isGenerating = false
        }
    }
    
    private func saveContent() {
        // Save to local database
    }
}

// MARK: - ViewModel

@MainActor
class AIViewModel: ObservableObject {
    @Published var user: User?
    @Published var contentItems: [ContentItem] = []
    @Published var isOffline = false
    
    private let client = SureshAIClient(apiVersion: "v2")
    private let offlineDB = OfflineDatabase()
    
    func login(email: String, password: String) async throws -> String {
        let token = try await client.auth.login(email: email, password: password)
        try await offlineDB.saveToken(token)
        return token
    }
    
    func generateContent(prompt: String, template: String) async throws -> String {
        let request = GenerateRequest(prompt: prompt, template: template)
        let response = try await client.content.generate(request)
        
        // Save offline copy
        let item = ContentItem(content: response.content, timestamp: Date())
        contentItems.append(item)
        try await offlineDB.saveContentItem(item)
        
        return response.content
    }
}

// MARK: - Models

struct User: Codable {
    let id: String
    let email: String
    let name: String
    let tier: String
}

struct ContentItem: Codable {
    let id: String = UUID().uuidString
    let content: String
    let timestamp: Date
    var isSynced: Bool = false
}

struct GenerateRequest: Codable {
    let prompt: String
    let template: String
}
"""

print("iOS Swift starter template created")
print("Setup: Create Xcode project, add SureshAI CocoaPod")
