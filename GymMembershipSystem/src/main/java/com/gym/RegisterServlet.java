package com.gym;

import java.io.IOException;
import java.sql.Connection;
import java.sql.Date;
import java.sql.PreparedStatement;
import java.sql.SQLException;
import java.sql.SQLIntegrityConstraintViolationException;

import javax.servlet.ServletException;
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

@WebServlet("/RegisterServlet")
public class RegisterServlet extends HttpServlet {
    private static final long serialVersionUID = 1L;

    protected void doPost(HttpServletRequest request, HttpServletResponse response) 
            throws ServletException, IOException {
        
        request.setCharacterEncoding("UTF-8");
        
        String name = request.getParameter("name");
        String email = request.getParameter("email");
        String phone = request.getParameter("phone");
        String password = request.getParameter("password");
        String membership = request.getParameter("membership");

        // Basic Server-Side Validation
        if (name == null || email == null || phone == null || password == null || membership == null ||
            name.trim().isEmpty() || email.trim().isEmpty() || phone.trim().isEmpty() || password.trim().isEmpty()) {
            response.sendRedirect("register.html?error=All fields are required");
            return;
        }

        if (phone.trim().length() != 10) {
            response.sendRedirect("register.html?error=Phone number must be exactly 10 digits");
            return;
        }

        if (password.length() < 6) {
            response.sendRedirect("register.html?error=Password must be at least 6 characters");
            return;
        }

        String sql = "INSERT INTO members (name, email, phone, password, membership, join_date, status) VALUES (?, ?, ?, ?, ?, ?, ?)";

        try (Connection conn = DBConnection.getConnection();
             PreparedStatement stmt = conn.prepareStatement(sql)) {

            if (conn == null) {
                response.sendRedirect("register.html?error=Database Connection Error");
                return;
            }

            stmt.setString(1, name.trim());
            stmt.setString(2, email.trim().toLowerCase());
            stmt.setString(3, phone.trim());
            stmt.setString(4, password);
            stmt.setString(5, membership.trim());
            stmt.setDate(6, new Date(System.currentTimeMillis()));
            stmt.setString(7, "Active");

            int rowsInserted = stmt.executeUpdate();

            if (rowsInserted > 0) {
                response.sendRedirect("login.html?registered=true");
            } else {
                response.sendRedirect("register.html?error=Registration failed. Please try again.");
            }

        } catch (SQLIntegrityConstraintViolationException e) {
            response.sendRedirect("register.html?error=Email address is already registered!");
        } catch (SQLException e) {
            e.printStackTrace();
            response.sendRedirect("register.html?error=Database error: " + e.getMessage());
        }
    }

    protected void doGet(HttpServletRequest request, HttpServletResponse response) 
            throws ServletException, IOException {
        response.sendRedirect("register.html");
    }
}
