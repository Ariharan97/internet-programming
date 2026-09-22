package com.gym;

import java.io.IOException;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;

import javax.servlet.ServletException;
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import javax.servlet.http.HttpSession;

@WebServlet("/LoginServlet")
public class LoginServlet extends HttpServlet {
    private static final long serialVersionUID = 1L;

    protected void doPost(HttpServletRequest request, HttpServletResponse response) 
            throws ServletException, IOException {
        
        request.setCharacterEncoding("UTF-8");
        
        String email = request.getParameter("email");
        String password = request.getParameter("password");

        if (email == null || password == null || email.trim().isEmpty() || password.trim().isEmpty()) {
            response.sendRedirect("login.html?error=Please enter both email and password");
            return;
        }

        String sql = "SELECT * FROM members WHERE email = ? AND password = ?";

        try (Connection conn = DBConnection.getConnection();
             PreparedStatement stmt = conn.prepareStatement(sql)) {

            if (conn == null) {
                response.sendRedirect("login.html?error=Database Connection Error");
                return;
            }

            stmt.setString(1, email.trim().toLowerCase());
            stmt.setString(2, password);

            try (ResultSet rs = stmt.executeQuery()) {
                if (rs.next()) {
                    // Login successful, create session
                    HttpSession session = request.getSession(true);
                    session.setAttribute("userEmail", rs.getString("email"));
                    session.setAttribute("userName", rs.getString("name"));
                    session.setAttribute("userId", rs.getInt("id"));

                    // Redirect to DashboardServlet
                    response.sendRedirect("DashboardServlet");
                } else {
                    // Invalid credentials
                    response.sendRedirect("login.html?error=Invalid email or password");
                }
            }

        } catch (SQLException e) {
            e.printStackTrace();
            response.sendRedirect("login.html?error=Database error occurred");
        }
    }

    protected void doGet(HttpServletRequest request, HttpServletResponse response) 
            throws ServletException, IOException {
        response.sendRedirect("login.html");
    }
}
