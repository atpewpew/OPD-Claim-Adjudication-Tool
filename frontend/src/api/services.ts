import { apiClient } from "./client";
import type {
  ClaimResponse,
  ClaimsListResponse,
  StatsResponse,
} from "./types";

export const claimsApi = {
  submitClaim: async (formData: FormData): Promise<ClaimResponse> => {
    const response = await apiClient.post<ClaimResponse>("/claims/", formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    });
    return response.data;
  },

  getClaims: async (skip = 0, limit = 100): Promise<ClaimsListResponse> => {
    const response = await apiClient.get<ClaimsListResponse>("/claims/", {
      params: { skip, limit },
    });
    return response.data;
  },

  getClaimById: async (id: string): Promise<ClaimResponse> => {
    const response = await apiClient.get<ClaimResponse>(`/claims/${id}`);
    return response.data;
  },

  getStats: async (): Promise<StatsResponse> => {
    const response = await apiClient.get<StatsResponse>("/claims/stats");
    return response.data;
  },
};
