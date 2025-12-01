# Requirements Document

## Introduction

This document outlines the requirements for a comprehensive set of platform enhancements to the home services marketplace. The enhancements include real-time notifications, online payment processing, scheduling calendar, portfolio management, improved geolocation, favorites system, analytics and reporting, mobile PWA capabilities, promotional system, and UX improvements. These features will improve user engagement, streamline operations, and provide a more professional experience for both clients and service providers.

## Glossary

- **Platform**: The home services marketplace web application
- **Client**: A user who searches for and hires service providers
- **Provider**: A service professional who offers services through the platform
- **Service Request**: A formal request from a client to hire a provider
- **Chat System**: The messaging interface between clients and providers
- **Dashboard**: The provider's control panel for managing services and business
- **PWA**: Progressive Web App - a web application that functions like a native mobile app
- **Real-time Notification**: An instant alert delivered to users when specific events occur
- **Payment Gateway**: Third-party service for processing online payments (Stripe/PagSeguro/Mercado Pago)
- **Portfolio**: A collection of photos and certificates showcasing a provider's previous work
- **Geolocation Service**: System for determining and displaying geographic locations
- **Favorite**: A saved reference to a provider that a client wants to remember
- **Coupon**: A promotional code that provides discounts on services
- **Analytics Dashboard**: Visual representation of business metrics and performance data

## Requirements

### Requirement 1: Real-time Notification System

**User Story:** As a client, I want to receive instant notifications about my service requests, so that I can respond quickly to provider actions and stay informed about my service status.

#### Acceptance Criteria

1. WHEN a provider accepts a service request, THE Platform SHALL send a real-time notification to the client within 2 seconds
2. WHEN a provider rejects a service request, THE Platform SHALL send a real-time notification to the client within 2 seconds
3. WHEN a new chat message arrives, THE Platform SHALL display a notification badge on the chat icon showing the unread message count
4. WHEN the service status changes, THE Platform SHALL send a real-time notification to the client with the updated status
5. THE Platform SHALL display notifications in a dropdown panel accessible from the navigation bar
6. THE Platform SHALL mark notifications as read when the user views them
7. THE Platform SHALL store notification history for at least 30 days

### Requirement 2: Real-time Notification System for Providers

**User Story:** As a provider, I want to receive instant notifications about new service requests and messages, so that I can respond promptly to potential clients.

#### Acceptance Criteria

1. WHEN a new service request is submitted, THE Platform SHALL send a real-time notification to the provider within 2 seconds
2. WHEN a client sends a chat message, THE Platform SHALL display a notification badge on the provider's chat icon
3. WHEN a client submits a review, THE Platform SHALL notify the provider within 2 seconds
4. THE Platform SHALL allow providers to configure notification preferences for different event types
5. THE Platform SHALL support browser push notifications when the user grants permission

### Requirement 3: Online Payment Processing

**User Story:** As a client, I want to pay for services securely through the platform, so that I have payment protection and a clear transaction record.

#### Acceptance Criteria

1. THE Platform SHALL integrate with at least one payment gateway (Stripe, PagSeguro, or Mercado Pago)
2. WHEN a client confirms a service, THE Platform SHALL present secure payment options including credit card and PIX
3. WHEN payment is successful, THE Platform SHALL update the service request status to "paid" within 5 seconds
4. THE Platform SHALL store transaction records with date, amount, payment method, and status
5. THE Platform SHALL display payment history in the client's dashboard
6. THE Platform SHALL hold funds in escrow until service completion is confirmed
7. WHEN service is completed, THE Platform SHALL release payment to the provider within 24 hours
8. IF payment fails, THEN THE Platform SHALL display a clear error message and allow retry

### Requirement 4: Provider Payment Management

**User Story:** As a provider, I want to view my earnings and transaction history, so that I can track my income and manage my finances.

#### Acceptance Criteria

1. THE Platform SHALL display total earnings, pending payments, and available balance in the provider dashboard
2. THE Platform SHALL show a detailed transaction history with filters by date range and status
3. THE Platform SHALL allow providers to configure payout preferences (bank account, PIX key)
4. THE Platform SHALL generate monthly earning reports in PDF format
5. THE Platform SHALL deduct platform commission (configurable percentage) from each transaction

### Requirement 5: Scheduling Calendar System

**User Story:** As a provider, I want to manage my availability through a visual calendar, so that I can prevent double-bookings and organize my schedule efficiently.

#### Acceptance Criteria

1. THE Platform SHALL display a monthly calendar view showing all scheduled services
2. THE Platform SHALL allow providers to block unavailable time slots by clicking on calendar dates
3. WHEN a client requests a service, THE Platform SHALL only show available time slots from the provider's calendar
4. THE Platform SHALL send automatic reminders 24 hours before scheduled appointments to both client and provider
5. THE Platform SHALL allow providers to set recurring unavailable periods (e.g., weekends, holidays)
6. THE Platform SHALL display different colors for confirmed, pending, and blocked time slots
7. THE Platform SHALL support drag-and-drop rescheduling of appointments

### Requirement 6: Portfolio and Photo Management

**User Story:** As a provider, I want to showcase my previous work with photos and certificates, so that I can build trust and attract more clients.

#### Acceptance Criteria

1. THE Platform SHALL allow providers to upload up to 20 portfolio photos with maximum size of 5MB each
2. THE Platform SHALL support JPEG, PNG, and WebP image formats
3. THE Platform SHALL allow providers to add captions and descriptions to each portfolio photo
4. THE Platform SHALL display portfolio photos in a grid gallery on the provider's profile page
5. THE Platform SHALL allow providers to upload professional certificates in PDF or image format
6. THE Platform SHALL support before/after photo pairs with side-by-side display
7. THE Platform SHALL automatically compress and optimize uploaded images for web display
8. THE Platform SHALL allow providers to reorder portfolio items by drag-and-drop

### Requirement 7: Enhanced Geolocation with Interactive Map

**User Story:** As a client, I want to see providers on an interactive map, so that I can easily find professionals near my location.

#### Acceptance Criteria

1. THE Platform SHALL display an interactive map on the search results page showing provider locations
2. THE Platform SHALL calculate and display the distance from the client's location to each provider
3. THE Platform SHALL allow clients to filter providers by service radius (5km, 10km, 20km, 50km)
4. WHEN a client clicks a map marker, THE Platform SHALL display a popup with provider name, rating, and quick link to profile
5. THE Platform SHALL automatically center the map on the client's current location when geolocation permission is granted
6. THE Platform SHALL update provider locations on the map in real-time as filters are applied
7. THE Platform SHALL display provider service areas as colored circles on the map

### Requirement 8: Favorites System

**User Story:** As a client, I want to save my favorite providers, so that I can easily find and hire them again in the future.

#### Acceptance Criteria

1. THE Platform SHALL display a heart icon on each provider's profile card and detail page
2. WHEN a client clicks the heart icon, THE Platform SHALL add the provider to the client's favorites list
3. THE Platform SHALL display a dedicated "My Favorites" page showing all saved providers
4. THE Platform SHALL show a visual indicator (filled heart) on favorited providers in search results
5. THE Platform SHALL allow clients to remove providers from favorites by clicking the heart icon again
6. THE Platform SHALL display the total count of favorites on the favorites page
7. THE Platform SHALL send a notification to providers when they are added to favorites (optional setting)

### Requirement 9: Analytics and Reporting Dashboard

**User Story:** As a provider, I want to view detailed analytics about my business performance, so that I can make data-driven decisions to improve my services.

#### Acceptance Criteria

1. THE Platform SHALL display a visual dashboard with charts showing service requests over time
2. THE Platform SHALL calculate and display average rating, total reviews, and response time metrics
3. THE Platform SHALL show revenue trends with monthly and yearly comparisons
4. THE Platform SHALL display the most requested services and peak booking times
5. THE Platform SHALL calculate conversion rate (requests received vs. requests accepted)
6. THE Platform SHALL allow providers to export analytics data in CSV format
7. THE Platform SHALL display client demographics (location distribution, repeat clients)
8. THE Platform SHALL show performance comparison against category averages

### Requirement 10: Progressive Web App (PWA)

**User Story:** As a user, I want to install the platform as a mobile app, so that I can access it quickly and receive push notifications.

#### Acceptance Criteria

1. THE Platform SHALL provide a web app manifest file with app name, icons, and theme colors
2. THE Platform SHALL implement a service worker for offline functionality
3. WHEN a user visits on mobile, THE Platform SHALL display an "Add to Home Screen" prompt
4. THE Platform SHALL cache essential pages and assets for offline viewing
5. THE Platform SHALL support push notifications when the user grants permission
6. THE Platform SHALL display a custom splash screen when launching the installed app
7. THE Platform SHALL work in standalone mode without browser UI when installed
8. THE Platform SHALL sync data automatically when connection is restored after offline use

### Requirement 11: Coupons and Promotions System

**User Story:** As a platform administrator, I want to create promotional campaigns with discount coupons, so that I can attract new users and increase engagement.

#### Acceptance Criteria

1. THE Platform SHALL allow administrators to create coupon codes with configurable discount percentages or fixed amounts
2. THE Platform SHALL support coupon validity periods with start and end dates
3. THE Platform SHALL allow setting usage limits (total uses and per-user limits)
4. WHEN a client applies a valid coupon, THE Platform SHALL display the discounted price before payment
5. THE Platform SHALL validate coupon codes and display clear error messages for invalid or expired coupons
6. THE Platform SHALL track coupon usage statistics including redemption count and total discount value
7. THE Platform SHALL support first-time user coupons that only work for new clients
8. THE Platform SHALL allow providers to create their own promotional coupons for their services

### Requirement 12: Referral Program

**User Story:** As a client, I want to refer friends to the platform and earn rewards, so that I can benefit from sharing the service.

#### Acceptance Criteria

1. THE Platform SHALL generate a unique referral code for each registered user
2. WHEN a new user signs up using a referral code, THE Platform SHALL credit both users with a discount coupon
3. THE Platform SHALL display referral statistics showing total referrals and earned rewards
4. THE Platform SHALL allow users to share their referral link via email, WhatsApp, and social media
5. THE Platform SHALL track the referral chain and attribute conversions correctly

### Requirement 13: UX Improvements - Loading States

**User Story:** As a user, I want to see clear loading indicators, so that I know the platform is processing my request.

#### Acceptance Criteria

1. WHEN data is loading, THE Platform SHALL display a spinner or skeleton screen within 100 milliseconds
2. THE Platform SHALL disable submit buttons during form processing to prevent double submissions
3. THE Platform SHALL display progress indicators for multi-step processes
4. THE Platform SHALL show loading states for image uploads with percentage completion
5. THE Platform SHALL display a loading overlay for full-page operations with descriptive text

### Requirement 14: UX Improvements - Error Handling

**User Story:** As a user, I want to see friendly and helpful error messages, so that I understand what went wrong and how to fix it.

#### Acceptance Criteria

1. WHEN an error occurs, THE Platform SHALL display a user-friendly message in Portuguese avoiding technical jargon
2. THE Platform SHALL provide specific guidance on how to resolve common errors
3. THE Platform SHALL display field-level validation errors next to the relevant input fields
4. THE Platform SHALL use consistent error styling with red color and warning icons
5. IF a critical error occurs, THEN THE Platform SHALL display a custom error page with navigation options

### Requirement 15: UX Improvements - Onboarding Tutorial

**User Story:** As a new user, I want to see a guided tutorial, so that I can quickly learn how to use the platform effectively.

#### Acceptance Criteria

1. WHEN a user registers for the first time, THE Platform SHALL display an interactive onboarding tutorial
2. THE Platform SHALL highlight key features with tooltips and overlay instructions
3. THE Platform SHALL allow users to skip the tutorial at any time
4. THE Platform SHALL provide separate tutorials for clients and providers based on user type
5. THE Platform SHALL display a progress indicator showing tutorial completion percentage
6. THE Platform SHALL allow users to replay the tutorial from their profile settings

### Requirement 16: UX Improvements - Complete Dark Mode

**User Story:** As a user, I want to use the platform in dark mode, so that I can reduce eye strain during nighttime usage.

#### Acceptance Criteria

1. THE Platform SHALL provide a dark mode toggle in the navigation bar or settings
2. THE Platform SHALL apply dark theme colors to all pages, components, and modals
3. THE Platform SHALL persist the user's theme preference across sessions
4. THE Platform SHALL automatically detect system theme preference on first visit
5. THE Platform SHALL ensure text contrast ratios meet WCAG AA standards in dark mode
6. THE Platform SHALL use smooth transitions when switching between light and dark modes
7. THE Platform SHALL apply dark mode to all third-party components and embedded content
