import React from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import Layout from "./components/Layout";
import Dashboard from "./pages/Dashboard";
import SubmitClaim from "./pages/SubmitClaim";
import ClaimDetail from "./pages/ClaimDetail";

export const App: React.FC = () => {
  return (
    <BrowserRouter>
      <Routes>
        {/* Redirect Root path to Dashboard */}
        <Route path="/" element={<Navigate to="/dashboard" replace />} />

        {/* Dashboard Route */}
        <Route
          path="/dashboard"
          element={
            <Layout>
              <Dashboard />
            </Layout>
          }
        />

        {/* Submit Claim Route */}
        <Route
          path="/submit"
          element={
            <Layout>
              <SubmitClaim />
            </Layout>
          }
        />

        {/* Claim Detail Route */}
        <Route
          path="/claim/:id"
          element={
            <Layout>
              <ClaimDetail />
            </Layout>
          }
        />

        {/* Fallback Route - Redirects all unknown paths to dashboard */}
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </BrowserRouter>
  );
};

export default App;
