"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";

export default function NotificationBell() {
  const [unreadCount, setUnreadCount] = useState(0);

  useEffect(() => {
    api
      .listNotifications()
      .then((notifications) => setUnreadCount(notifications.filter((n) => !n.is_read).length))
      .catch(() => {});
  }, []);

  return (
    <Link
      href="/notifications"
      className="relative rounded-md border border-border-subtle px-3 py-1.5 text-sm text-foreground/80 transition-colors hover:border-gold hover:text-gold-soft"
    >
      Notifications
      {unreadCount > 0 && (
        <span className="absolute -right-2 -top-2 flex h-5 min-w-5 items-center justify-center rounded-full bg-gold px-1 text-[11px] font-medium text-[#14140f]">
          {unreadCount}
        </span>
      )}
    </Link>
  );
}
