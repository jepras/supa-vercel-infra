drop policy "Users can only access their own activity logs" on "public"."activity_logs";

drop policy "Users can only access their own integrations" on "public"."integrations";

drop policy "Users can only access their own opportunity logs" on "public"."opportunity_logs";

revoke delete on table "public"."activity_logs" from "anon";

revoke insert on table "public"."activity_logs" from "anon";

revoke references on table "public"."activity_logs" from "anon";

revoke select on table "public"."activity_logs" from "anon";

revoke trigger on table "public"."activity_logs" from "anon";

revoke truncate on table "public"."activity_logs" from "anon";

revoke update on table "public"."activity_logs" from "anon";

revoke delete on table "public"."activity_logs" from "authenticated";

revoke insert on table "public"."activity_logs" from "authenticated";

revoke references on table "public"."activity_logs" from "authenticated";

revoke select on table "public"."activity_logs" from "authenticated";

revoke trigger on table "public"."activity_logs" from "authenticated";

revoke truncate on table "public"."activity_logs" from "authenticated";

revoke update on table "public"."activity_logs" from "authenticated";

revoke delete on table "public"."activity_logs" from "service_role";

revoke insert on table "public"."activity_logs" from "service_role";

revoke references on table "public"."activity_logs" from "service_role";

revoke select on table "public"."activity_logs" from "service_role";

revoke trigger on table "public"."activity_logs" from "service_role";

revoke truncate on table "public"."activity_logs" from "service_role";

revoke update on table "public"."activity_logs" from "service_role";

revoke delete on table "public"."integrations" from "anon";

revoke insert on table "public"."integrations" from "anon";

revoke references on table "public"."integrations" from "anon";

revoke select on table "public"."integrations" from "anon";

revoke trigger on table "public"."integrations" from "anon";

revoke truncate on table "public"."integrations" from "anon";

revoke update on table "public"."integrations" from "anon";

revoke delete on table "public"."integrations" from "authenticated";

revoke insert on table "public"."integrations" from "authenticated";

revoke references on table "public"."integrations" from "authenticated";

revoke select on table "public"."integrations" from "authenticated";

revoke trigger on table "public"."integrations" from "authenticated";

revoke truncate on table "public"."integrations" from "authenticated";

revoke update on table "public"."integrations" from "authenticated";

revoke delete on table "public"."integrations" from "service_role";

revoke insert on table "public"."integrations" from "service_role";

revoke references on table "public"."integrations" from "service_role";

revoke select on table "public"."integrations" from "service_role";

revoke trigger on table "public"."integrations" from "service_role";

revoke truncate on table "public"."integrations" from "service_role";

revoke update on table "public"."integrations" from "service_role";

revoke delete on table "public"."opportunity_logs" from "anon";

revoke insert on table "public"."opportunity_logs" from "anon";

revoke references on table "public"."opportunity_logs" from "anon";

revoke select on table "public"."opportunity_logs" from "anon";

revoke trigger on table "public"."opportunity_logs" from "anon";

revoke truncate on table "public"."opportunity_logs" from "anon";

revoke update on table "public"."opportunity_logs" from "anon";

revoke delete on table "public"."opportunity_logs" from "authenticated";

revoke insert on table "public"."opportunity_logs" from "authenticated";

revoke references on table "public"."opportunity_logs" from "authenticated";

revoke select on table "public"."opportunity_logs" from "authenticated";

revoke trigger on table "public"."opportunity_logs" from "authenticated";

revoke truncate on table "public"."opportunity_logs" from "authenticated";

revoke update on table "public"."opportunity_logs" from "authenticated";

revoke delete on table "public"."opportunity_logs" from "service_role";

revoke insert on table "public"."opportunity_logs" from "service_role";

revoke references on table "public"."opportunity_logs" from "service_role";

revoke select on table "public"."opportunity_logs" from "service_role";

revoke trigger on table "public"."opportunity_logs" from "service_role";

revoke truncate on table "public"."opportunity_logs" from "service_role";

revoke update on table "public"."opportunity_logs" from "service_role";

alter table "public"."activity_logs" drop constraint "activity_logs_user_id_fkey";

alter table "public"."integrations" drop constraint "integrations_user_id_fkey";

alter table "public"."integrations" drop constraint "integrations_user_id_provider_key";

alter table "public"."opportunity_logs" drop constraint "opportunity_logs_user_id_fkey";

alter table "public"."activity_logs" drop constraint "activity_logs_pkey";

alter table "public"."integrations" drop constraint "integrations_pkey";

alter table "public"."opportunity_logs" drop constraint "opportunity_logs_pkey";

drop index if exists "public"."activity_logs_pkey";

drop index if exists "public"."idx_activity_logs_activity_type";

drop index if exists "public"."idx_activity_logs_created_at";

drop index if exists "public"."idx_activity_logs_status";

drop index if exists "public"."idx_activity_logs_user_id";

drop index if exists "public"."idx_integrations_is_active";

drop index if exists "public"."idx_integrations_provider";

drop index if exists "public"."idx_integrations_user_id";

drop index if exists "public"."idx_opportunity_logs_created_at";

drop index if exists "public"."idx_opportunity_logs_email_hash";

drop index if exists "public"."idx_opportunity_logs_opportunity_detected";

drop index if exists "public"."idx_opportunity_logs_recipient_email";

drop index if exists "public"."idx_opportunity_logs_user_id";

drop index if exists "public"."integrations_pkey";

drop index if exists "public"."integrations_user_id_provider_key";

drop index if exists "public"."opportunity_logs_pkey";

drop table "public"."activity_logs";

drop table "public"."integrations";

drop table "public"."opportunity_logs";


