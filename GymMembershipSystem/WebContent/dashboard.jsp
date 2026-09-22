<%@ page language="java" contentType="text/html; charset=UTF-8" pageEncoding="UTF-8"%>
<%
    // Session validation security check
    if (session == null || session.getAttribute("userEmail") == null) {
        response.sendRedirect("login.html?error=Please login first");
        return;
    }

    String name = (String) request.getAttribute("memberName");
    String email = (String) request.getAttribute("memberEmail");
    String phone = (String) request.getAttribute("memberPhone");
    String plan = (String) request.getAttribute("memberPlan");
    Object joinDateObj = request.getAttribute("joinDate");
    String joinDate = (joinDateObj != null) ? joinDateObj.toString() : "N/A";
    String status = (String) request.getAttribute("status");
    if (status == null) status = "Active";
%>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Member Dashboard | FITNESS HUB</title>
    <link rel="stylesheet" href="css/style.css">
</head>
<body>

    <!-- Navigation Bar -->
    <nav class="navbar">
        <a href="index.html" class="logo">
            ⚡ FITNESS <span>HUB</span>
        </a>
        <ul class="nav-links">
            <li><a href="index.html">Home</a></li>
            <li><a href="DashboardServlet" class="active">Dashboard</a></li>
            <li><a href="LogoutServlet" class="nav-btn" style="background: rgba(255, 77, 77, 0.2); border: 1px solid rgba(255,77,77,0.4);">Logout</a></li>
        </ul>
    </nav>

    <!-- Dashboard Container -->
    <div class="dashboard-container">
        
        <!-- Welcome Header -->
        <div class="dashboard-header">
            <div class="user-welcome">
                <h2>WELCOME BACK, <span><%= (name != null) ? name.toUpperCase() : "MEMBER" %></span>! 👋</h2>
                <p>Here is your current FITNESS HUB membership portal overview</p>
            </div>
            <a href="LogoutServlet" class="btn-secondary" style="color: #ff6b6b; border-color: rgba(255,77,77,0.4);">
                🔒 Logout
            </a>
        </div>

        <!-- Dashboard Grid Layout -->
        <div class="dashboard-grid">
            
            <!-- Profile Details Card -->
            <div class="profile-card">
                <h3 class="card-title">👤 Member Profile Details</h3>
                
                <div class="info-grid">
                    <div class="info-item">
                        <span class="info-label">Full Name</span>
                        <span class="info-value"><%= (name != null) ? name : "N/A" %></span>
                    </div>

                    <div class="info-item">
                        <span class="info-label">Email Address</span>
                        <span class="info-value"><%= (email != null) ? email : "N/A" %></span>
                    </div>

                    <div class="info-item">
                        <span class="info-label">Phone Number</span>
                        <span class="info-value">+91 <%= (phone != null) ? phone : "N/A" %></span>
                    </div>

                    <div class="info-item">
                        <span class="info-label">Member Join Date</span>
                        <span class="info-value"><%= joinDate %></span>
                    </div>

                    <div class="info-item">
                        <span class="info-label">Membership Status</span>
                        <span class="status-badge"><%= status %></span>
                    </div>

                    <div class="info-item">
                        <span class="info-label">Access Pass</span>
                        <span class="info-value" style="color: #2ed573;">✓ 24/7 All-Access</span>
                    </div>
                </div>
            </div>

            <!-- Membership Summary Card -->
            <div class="membership-summary-card">
                <div>
                    <span class="hero-badge" style="margin-bottom: 1rem;">Current Subscription</span>
                    <h3 style="font-size: 1.8rem; margin-bottom: 0.5rem;"><%= (plan != null) ? plan : "Monthly" %> Plan</h3>
                    <p style="color: var(--text-secondary); font-size: 0.95rem; margin-bottom: 1.5rem;">
                        Your membership grants full access to cardio, strength equipment, and trainer consultations.
                    </p>
                </div>

                <div style="background: rgba(0,0,0,0.3); padding: 15px; border-radius: var(--radius-sm); border: 1px solid var(--border-color);">
                    <div style="font-size: 0.85rem; color: var(--text-muted);">ACCOUNT STATUS</div>
                    <div style="font-size: 1.1rem; font-weight: 700; color: #2ed573; margin-top: 2px;">
                        Active & In Good Standing
                    </div>
                </div>
            </div>

        </div>
    </div>

    <!-- Footer -->
    <footer>
        <p><strong>FITNESS HUB</strong> &copy; 2026. All Rights Reserved.</p>
    </footer>

    <script src="js/script.js"></script>
</body>
</html>
