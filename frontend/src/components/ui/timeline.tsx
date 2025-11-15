"use client";

import * as React from "react";
import { motion } from "motion/react";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";
import { ScrollArea } from "@/components/ui/scroll-area";
import {
  Check,
  Clock,
  X,
} from "lucide-react";

const timelineVariants = cva("relative flex flex-col", {
  variants: {
    variant: {
      default: "gap-4",
      compact: "gap-2",
      spacious: "gap-8",
    },
    orientation: {
      vertical: "flex-col",
      horizontal: "flex-row",
    },
  },
  defaultVariants: {
    variant: "default",
    orientation: "vertical",
  },
});

const timelineItemVariants = cva("relative flex gap-3 pb-2", {
  variants: {
    orientation: {
      vertical: "flex-row",
      horizontal: "flex-col min-w-64 shrink-0",
    },
  },
  defaultVariants: {
    orientation: "vertical",
  },
});

const timelineConnectorVariants = cva("bg-border", {
  variants: {
    orientation: {
      vertical: "absolute left-3 top-9 h-full w-px",
      horizontal: "absolute top-3 left-8 w-full h-px",
    },
    status: {
      default: "bg-border",
      completed: "bg-green-600",
      active: "bg-blue-500",
      pending: "bg-muted-foreground/50",
      error: "bg-destructive",
    },
  },
  defaultVariants: {
    orientation: "vertical",
    status: "default",
  },
});

const timelineIconVariants = cva(
  "flex h-6 w-6 shrink-0 items-center justify-center rounded-full border-2 bg-background text-xs font-medium",
  {
    variants: {
      status: {
        default: "border-border text-muted-foreground",
        completed: "border-green-600 bg-green-600 text-white",
        active: "border-blue-500 bg-background text-blue-500 animate-pulse",
        pending: "border-muted-foreground/50 text-muted-foreground/70",
        error: "border-destructive bg-destructive text-destructive-foreground",
      },
    },
    defaultVariants: {
      status: "default",
    },
  },
);

export interface TimelineItem {
  id: string;
  title: string;
  description?: string;
  timestamp?: string | Date;
  status?: "default" | "completed" | "active" | "pending" | "error";
  icon?: React.ReactNode;
  content?: React.ReactNode;
  metadata?: Record<string, any>;
}

export interface TimelineProps extends VariantProps<typeof timelineVariants> {
  items: TimelineItem[];
  className?: string;
  showConnectors?: boolean;
  showTimestamps?: boolean;
  timestampPosition?: "top" | "bottom" | "inline";
  isAnalyzing?: boolean;
}

function getStatusIcon(status: TimelineItem["status"]) {
  switch (status) {
    case "completed":
      return <Check className="h-3 w-3" />;
    case "active":
      return <Clock className="h-3 w-3" />;
    case "pending":
      return <Clock className="h-3 w-3" />;
    case "error":
      return <X className="h-3 w-3" />;
    default:
      return <div className="h-2 w-2 rounded-full bg-current" />;
  }
}

function formatTimestamp(timestamp: string | Date): string {
  if (!timestamp) return "";
  const date = typeof timestamp === "string" ? new Date(timestamp) : timestamp;
  return date.toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export function Timeline({
  items,
  className,
  variant,
  orientation = "vertical",
  showConnectors = true,
  showTimestamps = true,
  timestampPosition = "top",
  isAnalyzing = false,
  ...props
}: TimelineProps) {
  const timelineContent = (
    <div
      className={cn(
        timelineVariants({ variant, orientation }),
        orientation === "horizontal" ? "pb-4" : "",
      )}
    >
      {items.map((item, index) => (
        <div
          key={item.id}
          className={cn(timelineItemVariants({ orientation }))}
        >
          {/* Connector Line */}
          {showConnectors && index < items.length - 1 && (
            <motion.div
              className={cn(
                timelineConnectorVariants({
                  orientation,
                  // Don't apply completed status color when animating - let gradient handle it
                  status: item.status === "completed" && isAnalyzing ? undefined : item.status,
                }),
                // Add flowing gradient animation for completed lines during analysis
                item.status === "completed" && isAnalyzing && "animate-flowing-gradient"
              )}
              initial={{ scaleY: 0 }}
              animate={{ scaleY: 1 }}
              transition={{
                duration: 0.3,
                ease: "easeOut"
              }}
              layoutId={`connector-${item.id}`}
            />
          )}

          {/* Icon */}
          <div className="relative z-10 flex shrink-0">
            <div className={cn(timelineIconVariants({ status: item.status }))}>
              {item.icon || getStatusIcon(item.status)}
            </div>
          </div>

          {/* Content */}
          <div className="flex min-w-0 flex-1 flex-col gap-2">
            {/* Timestamp - Top */}
            {showTimestamps &&
              timestampPosition === "top" &&
              item.timestamp && (
                <time className="text-xs text-muted-foreground">
                  {formatTimestamp(item.timestamp)}
                </time>
              )}

            {/* Title and Inline Timestamp */}
            <div className="flex items-start justify-between gap-2">
              <h3 className="text-sm font-medium leading-tight">{item.title}</h3>
              {showTimestamps &&
                timestampPosition === "inline" &&
                item.timestamp && (
                  <time className="shrink-0 text-xs text-muted-foreground">
                    {formatTimestamp(item.timestamp)}
                  </time>
                )}
            </div>

            {/* Description */}
            {item.description && (
              <p className="text-xs text-muted-foreground leading-snug">
                {item.description}
              </p>
            )}

            {/* Custom Content */}
            {item.content && <div className="mt-3">{item.content}</div>}

            {/* Timestamp - Bottom */}
            {showTimestamps &&
              timestampPosition === "bottom" &&
              item.timestamp && (
                <time className="text-xs text-muted-foreground">
                  {formatTimestamp(item.timestamp)}
                </time>
              )}
          </div>
        </div>
      ))}
    </div>
  );

  if (orientation === "horizontal") {
    return (
      <ScrollArea
        orientation="horizontal"
        className={cn("w-full", className)}
        {...props}
      >
        {timelineContent}
      </ScrollArea>
    );
  }

  return (
    <div className={className} {...props}>
      {timelineContent}
    </div>
  );
}

export {
  timelineVariants,
  timelineItemVariants,
  timelineConnectorVariants,
  timelineIconVariants,
};
