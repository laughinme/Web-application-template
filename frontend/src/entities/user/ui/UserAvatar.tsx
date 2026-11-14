import { Avatar, AvatarFallback, AvatarImage } from "@/shared/ui/avatar";
import { initials } from "@/shared/lib/format";
import { cn } from "@/shared/lib/utils";
import { displayName, type User } from "../model/types";

export function UserAvatar({
  user,
  className,
}: {
  user: Pick<User, "username" | "email" | "avatarUrl">;
  className?: string;
}) {
  const name = displayName(user);
  return (
    <Avatar className={cn("size-9", className)}>
      {user.avatarUrl ? <AvatarImage src={user.avatarUrl} alt={name} /> : null}
      <AvatarFallback>{initials(name)}</AvatarFallback>
    </Avatar>
  );
}
