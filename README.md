# DjangoApp
Django Multi-App Social Media Application
Introduction
This Django-based social media application is designed to provide users with a platform for creating and sharing posts, interacting with others through comments and likes, and engaging in real-time chat with fellow users. The application is divided into three main apps: user, post, and chat, each serving distinct purposes. Below is a detailed README to help you set up and understand this multi-app social media platform.

Features
User Management (user app)

User Authentication: Users can create accounts, log in, and log out.
Registration: New users can sign up for an account.
Password Management: Users can change their passwords and reset forgotten passwords via email.
Custom User Model: The app uses a custom user model.
Email Verification: Newly registered users need to activate their accounts through email verification.
2FA (Two-Factor Authentication): Users can enable two-factor authentication for enhanced security.
Remember Me: Users can choose to remain logged in with the "Remember Me" option.
Auto-Logout: Users are automatically logged out after a specified inactivity period.
Post Sharing (post app)

Create Posts: Users can upload and share images.
Commenting: Users can comment on posts.
Liking: Users can like posts.
Real-Time Chat (chat app)

Chatrooms: Users can create chatrooms and invite other users.
Real-Time Chat: Users can engage in real-time chat using WebSockets.
Real-time Notifications: Users receive notifications for new chat messages via WebSockets.
