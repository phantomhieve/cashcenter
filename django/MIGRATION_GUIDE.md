# CashCenter Financial Year Migration Guide

This guide describes how to migrate your existing data to the new Financial Year system.

## Prerequisite
Ensure you have pulled the latest code which includes the `core` app and the `migrate_financial_years` management command.

## Migration Steps (Production)

### 1. Requirements
-   Backup your database before running any migration commands.

### 2. Apply Schema Changes
Run the standard Django migrate command to create the `FinancialYear` table and add the `financial_year` column to existing tables.
```bash
python manage.py migrate
```

### 3. Verify Migration (Dry Run)
Run the custom migration command in dry-run mode. This WILL NOT change any data but will print what it intends to do.
```bash
python manage.py migrate_financial_years --dry-run
```
**Check the output:**
-   Ensure it detects your "year-suffixed" users (e.g., `user@2021-2022`).
-   Ensure it plans to create the correct Financial Years.
-   Ensure it identifies "Orphan" entries in your base user (these will be assigned to the Current Financial Year).

### 4. Execute Migration
Once satisfied with the dry-run, execute the command for real.
```bash
python manage.py migrate_financial_years
```
**What this does:**
-   Consolidates `user@YYYY-YYYY` data into the main `user` account.
-   Tags that data with the appropriate `FinancialYear`.
-   Tags any unassigned data on the main `user` with the **Current Financial Year**.
-   Deactivates the old `user@YYYY-YYYY` accounts.

## Usage
-   Use the **Financial Year Dropdown** in the navbar to switch between years.
-   New data created will be assigned to the currently selected Financial Year.
