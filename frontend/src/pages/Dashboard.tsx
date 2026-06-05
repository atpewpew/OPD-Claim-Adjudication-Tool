import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { claimsApi } from "../api/services";
import type { ClaimResponse, StatsResponse } from "../api/types";
import { cn } from "../lib/utils";
import { 
  FileText, 
  CheckCircle2, 
  XCircle, 
  AlertCircle, 
  Search, 
  Filter, 
  ArrowRight,
  RefreshCw
} from "lucide-react";

export const Dashboard: React.FC = () => {
  const [claims, setClaims] = useState<ClaimResponse[]>([]);
  const [stats, setStats] = useState<StatsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // Search & Filtering State
  const [searchTerm, setSearchTerm] = useState("");
  const [statusFilter, setStatusFilter] = useState<string>("ALL");

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      // Fetch claims list
      const claimsRes = await claimsApi.getClaims(0, 100);
      setClaims(claimsRes.claims);

      // Fetch stats from backend
      try {
        const statsRes = await claimsApi.getStats();
        setStats(statsRes);
      } catch (err) {
        console.warn("Failed to fetch stats from API, calculating on frontend", err);
        // Defensive fallback: calculate stats from claims list
        const claimsList = claimsRes.claims;
        const total = claimsList.length;
        const approved = claimsList.filter(c => c.decision === "APPROVED").length;
        const rejected = claimsList.filter(c => c.decision === "REJECTED").length;
        const partial = claimsList.filter(c => c.decision === "PARTIAL").length;
        const manual = claimsList.filter(c => c.decision === "MANUAL_REVIEW").length;
        const totalApprovedAmount = claimsList.reduce((sum, c) => sum + (c.approved_amount || 0), 0);
        
        const validConfidences = claimsList.filter(c => c.confidence_score !== null);
        const avgConfidence = validConfidences.length 
          ? validConfidences.reduce((sum, c) => sum + (c.confidence_score || 0), 0) / validConfidences.length
          : 0;

        setStats({
          total,
          approved,
          rejected,
          partial,
          manual_review: manual,
          total_approved_amount: totalApprovedAmount,
          avg_confidence: avgConfidence
        });
      }
    } catch (err: any) {
      console.error("Error loading dashboard data:", err);
      setError("Failed to load claims database. Please ensure the backend server is running.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  // Format currency helpers
  const formatINR = (value: number | null | undefined) => {
    if (value === null || value === undefined) return "₹0";
    return new Intl.NumberFormat("en-IN", {
      style: "currency",
      currency: "INR",
      maximumFractionDigits: 0,
    }).format(value);
  };

  // Format date helper
  const formatDate = (dateStr: string) => {
    try {
      return new Date(dateStr).toLocaleDateString("en-IN", {
        day: "numeric",
        month: "short",
        year: "numeric",
      });
    } catch (e) {
      return dateStr;
    }
  };

  // Filtered Claims List
  const filteredClaims = claims.filter(claim => {
    const matchesSearch = 
      claim.member_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      claim.claim_id.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (claim.hospital_name || "").toLowerCase().includes(searchTerm.toLowerCase());
      
    const matchesStatus = 
      statusFilter === "ALL" || 
      claim.decision === statusFilter ||
      (statusFilter === "MANUAL_REVIEW" && claim.decision === "PARTIAL"); // Match yellow badges together if filtered

    return matchesSearch && matchesStatus;
  });

  return (
    <div className="space-y-8 animate-fadeIn">
      {/* Title & Refresh Button */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-900 md:text-3xl">Claims Operations</h1>
          <p className="text-sm text-slate-500 mt-1">
            Monitor, filter, and audit active OPD insurance claims and AI decisions.
          </p>
        </div>
        <button
          onClick={fetchData}
          disabled={loading}
          className="inline-flex items-center justify-center gap-2 px-4 py-2 text-sm font-medium text-slate-700 bg-white border border-slate-200 rounded-lg hover:bg-slate-50 active:bg-slate-100 transition-colors focus:outline-none focus:ring-2 focus:ring-violet-500/20 disabled:opacity-50"
        >
          <RefreshCw className={cn("h-4 w-4 text-slate-500", loading && "animate-spin")} />
          Refresh
        </button>
      </div>

      {/* Stats Section */}
      {loading ? (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="bg-white border border-slate-200 rounded-xl p-6 shadow-sm space-y-4">
              <div className="flex justify-between items-center">
                <div className="h-4 w-24 bg-slate-100 rounded animate-shimmer" />
                <div className="h-8 w-8 bg-slate-100 rounded-lg animate-shimmer" />
              </div>
              <div className="h-8 w-16 bg-slate-100 rounded animate-shimmer" />
              <div className="h-3 w-32 bg-slate-100 rounded animate-shimmer" />
            </div>
          ))}
        </div>
      ) : stats ? (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {/* Card 1: Total */}
          <div className="bg-white border-l-4 border-l-violet-500 border border-slate-200/80 rounded-xl p-5 shadow-sm hover:shadow-md transition-shadow duration-200 flex justify-between items-start">
            <div className="space-y-1.5">
              <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Total Submissions</span>
              <h3 className="text-3xl font-bold text-slate-900 font-sans tracking-tight">{stats.total}</h3>
              <p className="text-xs text-slate-400">Claims processed to date</p>
            </div>
            <div className="p-2.5 rounded-lg bg-violet-50 text-violet-600">
              <FileText className="h-5 w-5" />
            </div>
          </div>

          {/* Card 2: Approved */}
          <div className="bg-white border-l-4 border-l-emerald-500 border border-slate-200/80 rounded-xl p-5 shadow-sm hover:shadow-md transition-shadow duration-200 flex justify-between items-start">
            <div className="space-y-1.5">
              <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Approved Claims</span>
              <h3 className="text-3xl font-bold text-slate-900 font-sans tracking-tight">{stats.approved}</h3>
              <p className="text-xs text-emerald-600 font-medium">
                {stats.total > 0 ? Math.round((stats.approved / stats.total) * 100) : 0}% approval rate
              </p>
            </div>
            <div className="p-2.5 rounded-lg bg-emerald-50 text-emerald-600">
              <CheckCircle2 className="h-5 w-5" />
            </div>
          </div>

          {/* Card 3: Rejected */}
          <div className="bg-white border-l-4 border-l-rose-500 border border-slate-200/80 rounded-xl p-5 shadow-sm hover:shadow-md transition-shadow duration-200 flex justify-between items-start">
            <div className="space-y-1.5">
              <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Rejected Claims</span>
              <h3 className="text-3xl font-bold text-slate-900 font-sans tracking-tight">{stats.rejected}</h3>
              <p className="text-xs text-rose-600 font-medium">
                {stats.total > 0 ? Math.round((stats.rejected / stats.total) * 100) : 0}% rejection rate
              </p>
            </div>
            <div className="p-2.5 rounded-lg bg-rose-50 text-rose-600">
              <XCircle className="h-5 w-5" />
            </div>
          </div>

          {/* Card 4: Manual/Partial */}
          <div className="bg-white border-l-4 border-l-amber-500 border border-slate-200/80 rounded-xl p-5 shadow-sm hover:shadow-md transition-shadow duration-200 flex justify-between items-start">
            <div className="space-y-1.5">
              <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Pending Review</span>
              <h3 className="text-3xl font-bold text-slate-900 font-sans tracking-tight">
                {stats.manual_review + stats.partial}
              </h3>
              <p className="text-xs text-amber-600 font-medium">Requires operations audit</p>
            </div>
            <div className="p-2.5 rounded-lg bg-amber-50 text-amber-600">
              <AlertCircle className="h-5 w-5" />
            </div>
          </div>
        </div>
      ) : null}

      {/* Main Table Card */}
      <div className="bg-white border border-slate-200/80 rounded-xl shadow-sm overflow-hidden">
        {/* Table Header Controls */}
        <div className="p-5 border-b border-slate-200 bg-white flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="relative flex-1 max-w-md">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
            <input
              type="text"
              placeholder="Search by Member Name, Claim ID, or Hospital..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-9 pr-4 py-2 border border-slate-200 rounded-lg text-sm placeholder-slate-400 focus:outline-none focus:border-violet-500 focus:ring-2 focus:ring-violet-500/15"
            />
          </div>
          
          <div className="flex items-center gap-3 self-end md:self-auto">
            <Filter className="h-4 w-4 text-slate-400" />
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="px-3 py-2 border border-slate-200 rounded-lg text-sm bg-white font-medium text-slate-700 focus:outline-none focus:border-violet-500"
            >
              <option value="ALL">All Statuses</option>
              <option value="APPROVED">Approved Only</option>
              <option value="REJECTED">Rejected Only</option>
              <option value="PARTIAL">Partially Approved</option>
              <option value="MANUAL_REVIEW">Manual Review Only</option>
            </select>
          </div>
        </div>

        {/* Content State Handler */}
        {error ? (
          <div className="p-12 text-center">
            <div className="inline-flex p-3 rounded-full bg-rose-50 text-rose-600 mb-4">
              <AlertCircle className="h-6 w-6" />
            </div>
            <h3 className="text-base font-semibold text-slate-900">Database Connection Failed</h3>
            <p className="text-sm text-slate-500 mt-1 max-w-md mx-auto">{error}</p>
            <button
              onClick={fetchData}
              className="mt-4 px-4 py-2 text-sm font-medium text-white bg-violet-600 hover:bg-violet-700 active:bg-violet-800 rounded-lg transition-colors shadow-sm focus:outline-none"
            >
              Try Reconnecting
            </button>
          </div>
        ) : loading ? (
          <div className="divide-y divide-slate-100">
            {[...Array(6)].map((_, i) => (
              <div key={i} className="grid grid-cols-2 md:grid-cols-6 px-6 py-4 items-center gap-4">
                <div className="space-y-2 col-span-1">
                  <div className="h-3 w-16 bg-slate-100 rounded animate-shimmer" />
                  <div className="h-4 w-24 bg-slate-100 rounded animate-shimmer" />
                </div>
                <div className="h-4 w-28 bg-slate-100 rounded col-span-1 hidden md:block animate-shimmer" />
                <div className="h-4 w-24 bg-slate-100 rounded col-span-1 hidden md:block animate-shimmer" />
                <div className="h-4 w-20 bg-slate-100 rounded col-span-1 hidden md:block text-right animate-shimmer" />
                <div className="h-4 w-20 bg-slate-100 rounded col-span-1 hidden md:block text-right animate-shimmer" />
                <div className="h-6 w-20 bg-slate-100 rounded-full col-span-1 self-center justify-self-center animate-shimmer" />
              </div>
            ))}
          </div>
        ) : filteredClaims.length === 0 ? (
          <div className="p-16 text-center">
            <div className="inline-flex p-3 rounded-full bg-slate-50 text-slate-400 mb-4">
              <FileText className="h-6 w-6" />
            </div>
            <h3 className="text-base font-semibold text-slate-900">No Claims Found</h3>
            <p className="text-sm text-slate-500 mt-1">
              {claims.length === 0 
                ? "No claims have been submitted to the database yet." 
                : "No claims match your active search terms or filter criteria."}
            </p>
            {claims.length === 0 && (
              <Link
                to="/submit"
                className="inline-flex items-center gap-2 mt-4 px-4 py-2 text-sm font-medium text-white bg-violet-600 hover:bg-violet-700 rounded-lg transition-colors shadow-sm focus:outline-none"
              >
                Submit Your First Claim
                <ArrowRight className="h-4 w-4" />
              </Link>
            )}
          </div>
        ) : (
          <div className="overflow-x-auto">
            {/* Header Columns */}
            <div className="grid grid-cols-2 md:grid-cols-6 gap-4 px-6 py-3 bg-slate-50 border-b border-slate-200 text-xs font-semibold text-slate-500 uppercase tracking-wider select-none min-w-[700px]">
              <div>Claim ID / Member</div>
              <div>Hospital Name</div>
              <div>Treatment Date</div>
              <div className="text-right">Submitted</div>
              <div className="text-right">Approved</div>
              <div className="text-center">Status</div>
            </div>

            {/* List Rows */}
            <div className="divide-y divide-slate-100 min-w-[700px]">
              {filteredClaims.map((claim, idx) => {
                const isApproved = claim.decision === "APPROVED";
                const isRejected = claim.decision === "REJECTED";
                const isPartial = claim.decision === "PARTIAL";
                const isManual = claim.decision === "MANUAL_REVIEW";

                return (
                  <Link
                    key={claim.claim_id}
                    to={`/claim/${claim.claim_id}`}
                    style={{ animationDelay: `${idx * 30}ms` }}
                    className="grid grid-cols-2 md:grid-cols-6 gap-4 px-6 py-4 items-center hover:bg-slate-50/70 active:bg-slate-100/50 transition-all duration-150 text-slate-700 focus:outline-none focus:bg-slate-50 animate-fadeIn"
                  >
                    {/* ID & Member */}
                    <div className="flex flex-col gap-0.5">
                      <span className="font-mono text-xs font-bold text-slate-500 group-hover:text-violet-600">
                        {claim.claim_id.substring(0, 8)}...
                      </span>
                      <span className="font-medium text-slate-900">{claim.member_name}</span>
                    </div>

                    {/* Hospital Name */}
                    <div className="text-sm text-slate-600 truncate">
                      {claim.hospital_name || <span className="text-slate-400 italic">Non-network</span>}
                    </div>

                    {/* Date */}
                    <div className="text-sm text-slate-500">
                      {formatDate(claim.treatment_date)}
                    </div>

                    {/* Submitted Amount */}
                    <div className="text-right font-mono font-medium text-slate-900">
                      {formatINR(claim.submitted_amount)}
                    </div>

                    {/* Approved Amount */}
                    <div className="text-right font-mono font-medium text-slate-900">
                      {isApproved || isPartial ? (
                        <span className="text-emerald-600 font-semibold">{formatINR(claim.approved_amount)}</span>
                      ) : isRejected ? (
                        <span className="text-rose-500">—</span>
                      ) : (
                        <span className="text-slate-400 italic">Pending</span>
                      )}
                    </div>

                    {/* Badge */}
                    <div className="flex justify-center">
                      <span
                        className={cn(
                          "px-2.5 py-1 rounded-full text-xs font-semibold tracking-wide border transition-colors duration-150",
                          isApproved && "bg-emerald-50 text-emerald-700 border-emerald-200/60",
                          isRejected && "bg-rose-50 text-rose-700 border-rose-200/60",
                          isPartial && "bg-amber-50 text-amber-700 border-amber-200/60",
                          isManual && "bg-indigo-50 text-indigo-700 border-indigo-200/60"
                        )}
                      >
                        {claim.decision.replace("_", " ")}
                      </span>
                    </div>
                  </Link>
                );
              })}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Dashboard;
