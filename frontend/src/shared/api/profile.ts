import apiProtected from "./axiosInstance";
import { toUser, toUserPatchDto } from "@/entities/user/model";
import type { User, UserPatchPayload } from "@/entities/user/model";

export type UserDto = {
    id: string;
    email: string;
    username: string | null;
    profile_pic_url: string | null;
    bio: string | null;
    is_onboarded: boolean;
    banned: boolean;
    role_slugs: string[];
    created_at: string;
    updated_at: string | null;
};

export type UserPatchPayloadDto = {
    username?: string | null;
    bio?: string | null;
};

export const getProfile = async (): Promise<User> => {
    const response = await apiProtected.get<UserDto>("/users/me");
    return toUser(response.data);
};

export const patchProfile = async (
    data: UserPatchPayload
): Promise<User> => {
    const dto = toUserPatchDto(data);
    const response = await apiProtected.patch<UserDto>("/users/me", dto);
    return toUser(response.data);
};

export const uploadProfilePicture = async (
    file: File
): Promise<User> => {
    const formData = new FormData();
    formData.append("file", file);
    const response = await apiProtected.put<UserDto>(
        "/users/me/picture",
        formData,
        { headers: { "Content-Type": "multipart/form-data" } }
    );
    return toUser(response.data);
};
