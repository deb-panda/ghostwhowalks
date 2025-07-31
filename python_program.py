import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import matplotlib.backends.backend_pdf as backend_pdf
import matplotlib.gridspec as gridspec
from matplotlib.backends.backend_pdf import PdfPages
from pandas.tseries.offsets import BDay
import os


# ==== CONFIGURATION ====
CONFIG = {
    "trade_size": 100_000,
    "initial_capital": 10_00_000,
    "max_trades_per_day": 2,
    "thresholds": [-10,-5, 5, 10, 15, 20],
    "exit_conditions": {
        "target_pct": 5,
        "stoploss_pct": -10,
        "timeout_days": 180,
    },
    "csv_file": '/workspaces/ghostwhowalks/test_data.csv',
    "output_folder": '/workspaces/ghostwhowalks/output'
}


def read_csv_data(csv_file):
    def parse_date(x):
        try:
            return pd.to_datetime(x).normalize()
        except:
            return pd.NaT

    df = pd.read_csv(csv_file)
    df['date'] = df['date'].apply(parse_date)
    return df



def configure_data_frame():
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 1000)
    pd.set_option('display.max_colwidth', None)

def create_csv(df, path, file_name):
    full_path = os.path.join(CONFIG["output_folder"], file_name)
    df.to_csv(full_path, index=False)
    #df.to_csv(f'/content/drive/My Drive/{path}/{file_name}', index=False)

def calculate_thresholds(df, thresholds):
    target_pct = CONFIG["exit_conditions"]["target_pct"]
    stoploss_pct = CONFIG["exit_conditions"]["stoploss_pct"]
    results = []
    threshold_stats = {t: {'count': 0, 'days_list': []} for t in thresholds}


    for _, row in df.iterrows():
        symbol = row['symbol'].strip().upper() + '.NS'

        entry_date = pd.to_datetime(row['date']) + BDay(1)
        print(f"\n🔍 Processing {symbol} from {entry_date.date()}")

        try:
            data = yf.download(symbol, start=entry_date, end=entry_date + timedelta(days=90), progress=False, auto_adjust=True)

            if data.empty or pd.Timestamp(entry_date) not in data.index:
                print(f"⚠️  No data for {symbol} on {entry_date.date()}")
                continue

            entry_price = data.loc[pd.Timestamp(entry_date), 'Close']
            reached = {t: None for t in thresholds}
            reached_dates = {t: None for t in thresholds}

            for date, row_data in data.iterrows():
                try:
                    high_price = float(row_data['High'])
                    pct_change = float((high_price - entry_price) / entry_price * 100)
                    for t in thresholds:
                        if reached[t] is None:
                            if (t > 0 and pct_change >= t) or (t < 0 and pct_change <= t):
                                reached[t] = (date - entry_date).days
                                reached_dates[t] = date.date()
                except Exception as e:
                    print(f"  ⚠️  Skipping {date.date()} due to error: {e}")

            for t in thresholds:
                if reached[t] is not None:
                    threshold_stats[t]['count'] += 1
                    threshold_stats[t]['days_list'].append(reached[t])

            results.append({
                'symbol': row['symbol'],
                'entry_date': pd.to_datetime(row['date']).date(),
                'actual_entry_date': entry_date.date(),
                **{f'days_to_+{target_pct}%': reached[target_pct], f'days_to_{stoploss_pct:+}%': reached[stoploss_pct]},
                **{f'date_to_+{target_pct}%': reached_dates[target_pct], f'date_to_{stoploss_pct:+}%': reached_dates[stoploss_pct]},
            })

        except Exception as e:
            print(f"❌ Error processing {symbol}: {e}")


    return pd.DataFrame(results), threshold_stats

def plot_threshold_summary(threshold_stats, total_stocks):
    print("\n📊 Threshold Summary Metrics")
    for t, stats in threshold_stats.items():
        count = stats['count']
        pct = (count / total_stocks) * 100 if total_stocks > 0 else 0
        avg_days = (sum(stats['days_list']) / len(stats['days_list'])) if stats['days_list'] else None
        print(f"➡ Threshold {t:+}% | Hit by: {count} stocks ({pct:.1f}%)" + (f" | Avg Days: {avg_days:.2f}" if avg_days else " | Not hit"))

    labels = [f"{t:+}%" for t in threshold_stats]
    counts = [threshold_stats[t]['count'] for t in threshold_stats]
    plt.figure(figsize=(8, 5))
    plt.bar(labels, counts, color='skyblue')
    plt.title('Stocks Reaching Each Threshold')
    plt.xlabel('Threshold (%)')
    plt.ylabel('Number of Stocks')
    plt.grid(True, axis='y', linestyle='--', alpha=0.7)
    plt.show()

def calculate_win_rate(df):
    wins = 0
    for _, row in df.iterrows():
        target_pct = CONFIG["exit_conditions"]["target_pct"]
        stoploss_pct = CONFIG["exit_conditions"]["stoploss_pct"]
        up = row.get(f'days_to_+{target_pct}%')
        down = row.get(f'days_to_{stoploss_pct:+}%')
        if pd.notna(up) and (pd.isna(down) or up < down):
            wins += 1
    win_pct = (wins / len(df)) * 100 if len(df) > 0 else 0
    print(f"🏁 Overall Win Rate: {wins}/{len(df)} = {win_pct:.2f}%")
    return win_pct

def simulate_equity_curve(df):
    initial_capital = CONFIG["initial_capital"]
    capital = initial_capital
    trade_size = CONFIG["trade_size"]
    max_trades_per_day = CONFIG["max_trades_per_day"]
    daily_capital_curve = {}
    forced_exit_count = 0

    df['actual_entry_date'] = pd.to_datetime(df['actual_entry_date'])
    grouped = df.groupby('actual_entry_date')

    timeout_days = CONFIG["exit_conditions"]["timeout_days"]

    for date, group in grouped:
        trades_today = 0
        for _, row in group.iterrows():
            if trades_today >= max_trades_per_day or capital < trade_size:
                continue

            target_pct = CONFIG["exit_conditions"]["target_pct"]
            stoploss_pct = CONFIG["exit_conditions"]["stoploss_pct"]
            up = row.get(f'days_to_+{target_pct}%')
            down = row.get(f'days_to_{stoploss_pct:+}%')

            if pd.notna(up) and (pd.isna(down) or up < down):
                pnl = trade_size * (CONFIG["exit_conditions"]["target_pct"] / 100)
            elif pd.notna(down):
                pnl = -trade_size * abs(CONFIG["exit_conditions"]["stoploss_pct"] / 100)
            else:
                symbol = row['symbol'].strip().upper() + '.NS'
                entry_date = pd.to_datetime(row['actual_entry_date'])
                exit_date = entry_date + timedelta(days=timeout_days)
                forced_exit_count += 1
                try:
                    price_data = yf.download(symbol, start=entry_date, end=exit_date + timedelta(days=1), progress=False, auto_adjust=True)
                    if not price_data.empty:
                        if exit_date in price_data.index:
                            exit_price = price_data.loc[exit_date, 'Close'].item()
                        else:
                            exit_price = price_data.iloc[-1]['Close'].item()
                        entry_price = price_data.iloc[0]['Close'].item()
                        return_pct = (exit_price - entry_price) / entry_price
                        pnl = trade_size * return_pct
                    else:
                        pnl = 0
                except:
                    pnl = 0

            capital += pnl
            trades_today += 1

        daily_capital_curve[date.date()] = capital

    print(f"🚪 Trades exited after 60-day timeout: {forced_exit_count}")
    return capital, initial_capital, pd.Series(daily_capital_curve).sort_index()


def calculate_expected_payoff(df):
    wins = losses = 0
    win_amt = CONFIG["trade_size"] * (CONFIG["exit_conditions"]["target_pct"] / 100)
    loss_amt = CONFIG["trade_size"] * abs(CONFIG["exit_conditions"]["stoploss_pct"] / 100)

    for _, row in df.iterrows():
        target_pct = CONFIG["exit_conditions"]["target_pct"]
        stoploss_pct = CONFIG["exit_conditions"]["stoploss_pct"]
        up = row.get(f'days_to_+{target_pct}%')
        down = row.get(f'days_to_{stoploss_pct:+}%')

        if pd.notna(up) and (pd.isna(down) or up < down):
            wins += 1
        elif pd.notna(down):
            losses += 1
    expected_payoff = (wins * win_amt - losses * loss_amt) / len(df) if len(df) > 0 else 0
    print(f"\n💡 Expected Payoff per Trade: ₹{expected_payoff:.2f}")
    return expected_payoff

def generate_trade_summary_df(df):
    trade_size = CONFIG["trade_size"]
    summary_rows = []
    timeout_days = CONFIG["exit_conditions"]["timeout_days"]

    print(df)

    for _, row in df.iterrows():
        symbol = row['symbol'].strip().upper() + '.NS'
        purchase_date = pd.to_datetime(row['actual_entry_date'])
        sell_date = None
        entry_price = None
        exit_price = None
        profit_pct = 0
        pnl = 0
        reason = ""

        try:
            data = yf.download(symbol, start=purchase_date, end=purchase_date + timedelta(days=61), progress=False, auto_adjust=True)  #TODO - Change days in timedelta to configurable
            if data.empty:
                continue
            entry_price = float(data.iloc[0]['Close'])

            target_pct = CONFIG["exit_conditions"]["target_pct"]
            stoploss_pct = CONFIG["exit_conditions"]["stoploss_pct"]
            up_day = row.get(f'days_to_+{target_pct}%')
            down_day = row.get(f'days_to_{stoploss_pct:+}%')


            if pd.notna(up_day) and (pd.isna(down_day) or up_day < down_day):
                sell_date = purchase_date + timedelta(days=int(up_day))
                reason = f"Target +{target_pct}%"
                exit_price = float(data.loc[sell_date]['Close']) if sell_date in data.index else float(data.iloc[-1]['Close'])
            elif pd.notna(down_day):
                sell_date = purchase_date + timedelta(days=int(down_day))
                reason = f"Stoploss {stoploss_pct:+}%"
                exit_price = float(data.loc[sell_date]['Close']) if sell_date in data.index else float(data.iloc[-1]['Close'])
            else:
                sell_date = purchase_date + timedelta(days=timeout_days)
                reason = "Timed Exit"
                exit_price = float(data.loc[sell_date]['Close']) if sell_date in data.index else float(data.iloc[-1]['Close'])

            profit_pct = ((exit_price - entry_price) / entry_price) * 100
            pnl = (exit_price - entry_price) * (trade_size / entry_price)

        except Exception as e:
            print(f"⚠️ Skipping {symbol} due to error: {e}")
            continue

        summary_rows.append({
            'symbol': row['symbol'],
            'purchase_date': purchase_date.date(),
            'purchase_price': round(entry_price, 2) if entry_price else None,
            'sell_date': sell_date.date() if sell_date else None,
            'sell_price': round(exit_price, 2) if exit_price else None,
            'profit_pct': round(profit_pct, 2),
            'pnl': round(pnl, 2),
            'exit_reason': reason
        })

    return pd.DataFrame(summary_rows)

def calculate_max_drawdown(equity_series):
    peak = equity_series[0]
    max_drawdown = 0
    for value in equity_series:
        if value > peak:
            peak = value
        drawdown = peak - value
        max_drawdown = max(max_drawdown, drawdown)
    max_drawdown_pct = (max_drawdown / peak) * 100 if peak > 0 else 0
    print(f"\n🔻 Max Drawdown: ₹{max_drawdown:,.2f} ({max_drawdown_pct:.2f}%)")
    return max_drawdown, max_drawdown_pct


def plot_monthly_profit_loss(df):
    df['actual_entry_date'] = pd.to_datetime(df['actual_entry_date'])
    timeout_days = CONFIG["exit_conditions"]["timeout_days"]

    trade_size = CONFIG["trade_size"]
    max_trades_per_day = 2
    capital = CONFIG["initial_capital"]
    month_pnl = {}

    grouped = df.groupby('actual_entry_date')

    for date, group in grouped:
        trades_today = 0
        for _, row in group.iterrows():
            if trades_today >= max_trades_per_day or capital < trade_size:
                continue

            entry_date = pd.to_datetime(row['actual_entry_date'])
            pnl = 0
            target_pct = CONFIG["exit_conditions"]["target_pct"]
            stoploss_pct = CONFIG["exit_conditions"]["stoploss_pct"]
            up = row.get(f'days_to_+{target_pct}%')
            down = row.get(f'days_to_{stoploss_pct:+}%')


            if pd.notna(up) and (pd.isna(down) or up < down):
                pnl = trade_size * (CONFIG["exit_conditions"]["target_pct"] / 100)
            elif pd.notna(down):
                pnl = -trade_size * abs(CONFIG["exit_conditions"]["stoploss_pct"] / 100)
            else:
                symbol = row['symbol'].strip().upper() + '.NS'
                exit_date = entry_date + timedelta(days=timeout_days)
                try:
                    price_data = yf.download(symbol, start=entry_date, end=exit_date + timedelta(days=1), progress=False, auto_adjust=True)
                    if not price_data.empty:
                        if exit_date in price_data.index:
                            exit_price = float(price_data.loc[exit_date, 'Close'])
                        else:
                            exit_price = float(price_data.iloc[-1]['Close'])
                        entry_price = float(price_data.iloc[0]['Close'])
                        return_pct = (exit_price - entry_price) / entry_price
                        pnl = return_pct * trade_size
                except:
                    pnl = 0

            capital += pnl
            trades_today += 1

            month_key = entry_date.to_period('M').strftime('%Y-%m')
            month_pnl[month_key] = month_pnl.get(month_key, 0) + pnl

    # Plot
    pnl_series = pd.Series(month_pnl).sort_index()
    plt.figure(figsize=(12, 5))
    sns.barplot(x=pnl_series.index, y=pnl_series.values, palette='coolwarm')
    plt.title("📅 Month-wise P&L (with max 2 trades/day and 60-day exit, capital limited)")
    plt.xlabel("Month")
    plt.ylabel("Profit / Loss (INR)")
    plt.xticks(rotation=45)
    plt.axhline(0, color='black', linestyle='--')
    plt.tight_layout()
    plt.show()

    return month_pnl

def export_backtest_summary_to_single_page_pdf(
    threshold_stats, total_stocks, month_pnl,
    final_capital, initial_capital, win_pct, expected_payoff, max_drawdown,
    equity_curve,cagr,
    output_path='/content/drive/My Drive/output/threshold_summary.pdf',
    pdf_title='BACKTEST SUMMARY'
):
    import matplotlib.pyplot as plt
    import matplotlib.gridspec as gridspec
    from matplotlib.backends.backend_pdf import PdfPages
    import seaborn as sns
    import pandas as pd

    sns.set_style("whitegrid")

    with PdfPages(output_path) as pdf:
        fig = plt.figure(figsize=(14, 18))
        fig.suptitle(pdf_title.upper(), fontsize=20, fontweight='bold', color='darkblue', y=0.995)
        fig.text(0.5, 0.975, f"Generated on: {datetime.now().strftime('%d %b %Y %H:%M')}", fontsize=10, color='gray', ha='center')

        spec = gridspec.GridSpec(nrows=5, ncols=2, figure=fig, height_ratios=[1, 1, 1.2, 1, 1.2])

        # --- Row 1: Backtest Summary Table ---
        ax_table = fig.add_subplot(spec[0, 0])
        backtest_summary_data = {
            'Metric': [
                'Amount / trade',
                'Exit Criteria',
                'Initial Capital',
                'Final Capital',
                'Net P & L',
                'CAGR',
                'Overall Win %',
                'Expected Payoff',
                'Max Drawdown',
            ],
            'Value': [
                f'{CONFIG["trade_size"]}',
                f'{CONFIG["exit_conditions"]["stoploss_pct"]:+}%, +{CONFIG["exit_conditions"]["target_pct"]}%, {CONFIG["exit_conditions"]["timeout_days"]} days',
                f'₹{initial_capital:,.0f}',
                f'₹{final_capital:,.0f}',
                f'₹{final_capital - initial_capital:,.0f}',
                f'{cagr:.2f}%',
                f'{win_pct:.2f}%',
                f'₹{expected_payoff:.2f}',
                f'₹{max_drawdown[0]:,.0f} ({max_drawdown[1]:.2f}%)'
            ]
        }
        df_summary = pd.DataFrame(backtest_summary_data)
        ax_table.axis('off')
        table = ax_table.table(cellText=df_summary.values, colLabels=df_summary.columns, loc='center')
        table.auto_set_font_size(False)
        table.set_fontsize(11)
        table.scale(1.2, 1.4)
        ax_table.set_title('📋 Backtest Summary', fontsize=14, fontweight='bold', loc='left')

        # --- Row 1, Column 2: Win % Circle Display ---
        ax_circle = fig.add_subplot(spec[0, 1])
        ax_circle.axis('off')

        # Draw green circle
        circle = plt.Circle((0.5, 0.5), 0.4, color='green', transform=ax_circle.transAxes)
        ax_circle.add_patch(circle)

        # Display Win % in center of circle
        ax_circle.text(0.5, 0.5, f"{win_pct:.1f}%", fontsize=28, fontweight='bold',
                      color='white', ha='center', va='center')

        # Optional: Title above the circle
        ax_circle.text(0.5, 0.9, "🏆 WIN RATE", fontsize=12, fontweight='bold',
                      color='darkgreen', ha='center', transform=ax_circle.transAxes)


        # --- Row 2: Threshold Summary Table ---
        ax_table2 = fig.add_subplot(spec[1, :])
        threshold_rows = []
        for i, (t, stats) in enumerate(threshold_stats.items()):
            count = stats['count']
            pct = (count / total_stocks) * 100 if total_stocks > 0 else 0
            avg_days = (sum(stats['days_list']) / len(stats['days_list'])) if stats['days_list'] else None
            threshold_rows.append([
                f"{t:+}%",
                count,
                f"{pct:.1f}%",
                f"{avg_days:.2f}" if avg_days else "N/A"
            ])

        df_thresholds = pd.DataFrame(threshold_rows, columns=['Threshold', 'Hit Count', 'Hit %', 'Avg Days'])
        ax_table2.axis('off')
        table2 = ax_table2.table(cellText=df_thresholds.values, colLabels=df_thresholds.columns, loc='center')
        table2.auto_set_font_size(False)
        table2.set_fontsize(11)
        table2.scale(1.2, 1.4)
        ax_table2.set_title('🎯 Threshold Summary', fontsize=14, fontweight='bold', loc='left')

        # --- Row 3: Threshold Hit Bar Chart ---
        ax_chart1 = fig.add_subplot(spec[2, :])
        labels = [f"{t:+}%" for t in threshold_stats]
        counts = [threshold_stats[t]['count'] for t in threshold_stats]
        bars = ax_chart1.bar(labels, counts, color='skyblue')
        for bar in bars:
            height = bar.get_height()
            ax_chart1.annotate(f'{height}', xy=(bar.get_x() + bar.get_width()/2, height),
                               xytext=(0, 3), textcoords="offset points", ha='center', fontsize=9)
        ax_chart1.set_title('📊 Stocks Reaching Each Threshold', fontsize=13, fontweight='bold')
        ax_chart1.set_xlabel('Threshold (%)')
        ax_chart1.set_ylabel('Number of Stocks')
        ax_chart1.grid(True, axis='y', linestyle='--', alpha=0.7)

        # --- Row 4: Month-wise P&L ---
        ax_chart2 = fig.add_subplot(spec[3, :])
        pnl_series = pd.Series(month_pnl).sort_index()
        sns.barplot(x=pnl_series.index, y=pnl_series.values, ax=ax_chart2, palette='coolwarm')
        for i, val in enumerate(pnl_series.values):
            ax_chart2.text(i, val + (500 if val >= 0 else -1000), f'{int(val):,}', ha='center', va='bottom' if val >= 0 else 'top', fontsize=8)
        ax_chart2.set_title("📅 Month-wise P&L", fontsize=13, fontweight='bold')
        ax_chart2.set_xlabel("Month")
        ax_chart2.set_ylabel("Profit / Loss (INR)")
        ax_chart2.tick_params(axis='x', rotation=45)
        ax_chart2.axhline(0, color='black', linestyle='--', linewidth=0.8)
        ax_chart2.grid(True, axis='y', linestyle='--', alpha=0.5)

        # --- Row 5: Equity Curve ---
        ax_equity = fig.add_subplot(spec[4, :])
        equity_curve.plot(ax=ax_equity, marker='o', color='blue', linewidth=2)
        ax_equity.set_title("📈 Equity Curve Over Time", fontsize=13, fontweight='bold')
        ax_equity.set_xlabel("Date")
        ax_equity.set_ylabel("Capital (INR)")
        ax_equity.axhline(initial_capital, color='gray', linestyle='--', linewidth=1, label="Initial Capital")
        ax_equity.legend([f"Final Capital: ₹{final_capital:,.0f} (+{(final_capital-initial_capital)/initial_capital*100:.1f}%)"], loc='upper left')
        ax_equity.grid(True, linestyle='--', alpha=0.6)
        ax_equity.tick_params(axis='x', rotation=45)

        plt.tight_layout(rect=[0, 0, 1, 0.96])
        pdf.savefig(fig)
        plt.close(fig)

def calculate_cagr(initial_capital, final_capital, equity_curve):
    try:
        start_date = equity_curve.index[0]
        end_date = equity_curve.index[-1]
        num_days = (end_date - start_date).days
        num_years = num_days / 365.25  # account for leap years

        if num_years <= 0:
            return 0.0

        cagr = ((final_capital / initial_capital) ** (1 / num_years)) - 1
        print(f"\n📈 CAGR: {cagr * 100:.2f}% over {num_years:.2f} years")
        return cagr * 100
    except Exception as e:
        print(f"⚠️ Error calculating CAGR: {e}")
        return 0.0




def main():
    #csv_file = '/content/drive/MyDrive/backtest_data/hm_backtest_v2.csv'
    #csv_file = '/content/drive/MyDrive/backtest_data/deb_hm_3ma_daily.csv'
    #csv_file = '/content/drive/MyDrive/backtest_data/deb_hm_3ma_weekly.csv'
    #csv_file = '/content/drive/MyDrive/backtest_data/deb_hm_3ma_weekly_v2.csv'
    #csv_file = '/content/drive/MyDrive/backtest_data/gfs.csv'
    #csv_file = '/content/drive/MyDrive/backtest_data/deb_hm_gapup.csv'
    #csv_file = '/content/drive/MyDrive/backtest_data/deb_hm.csv'
    #csv_file = '/content/drive/MyDrive/backtest_data/hm_weekly.csv'
    #csv_file = '/content/drive/MyDrive/backtest_data/deb_basket.csv'

    csv_file = CONFIG["csv_file"]
    target_pct = CONFIG["exit_conditions"]["target_pct"]
    stoploss_pct = CONFIG["exit_conditions"]["stoploss_pct"]
    # thresholds: include both positive and negative
    thresholds = sorted(set(CONFIG["thresholds"] + [target_pct, stoploss_pct]))



    configure_data_frame()
    df = read_csv_data(csv_file)

    # Remove duplicate stock entries (keep first)
    df = df.sort_values(by='date')  # optional, to prioritize earliest entry
    df = df.drop_duplicates(subset='symbol', keep='first')



    # Extract name from CSV and timestamp
    csv_name = os.path.basename(csv_file).replace('.csv', '')
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    pdf_filename = f"Backtest_Summary_{csv_name}_{timestamp}.pdf"
    pdf_output_path = os.path.join(CONFIG["output_folder"], pdf_filename)



    # Step 1: Calculate thresholds
    output_df, threshold_stats = calculate_thresholds(df, thresholds)

    # Step 1.5 : Create trade details
    trade_summary_df = generate_trade_summary_df(output_df)
    create_csv(trade_summary_df, 'output', f'backtest_{csv_name}_{timestamp}.csv')


    # Step 2: Global summary (no yearly split)
    output_df['actual_entry_date'] = pd.to_datetime(output_df['actual_entry_date'])

    print(f"\n📦 Total Trades: {len(output_df)}")

    # Threshold summary
    plot_threshold_summary(threshold_stats, len(output_df))

    # Step 3: Capital Simulation
    final_capital, initial_capital, equity_curve = simulate_equity_curve(output_df)
    print(f"\n💰 Final Capital: ₹{final_capital:,.2f}")
    print(f"📈 Net P&L: ₹{final_capital - initial_capital:,.2f}")

    # Equity Curve Plot — Full Duration
    plt.figure(figsize=(12, 5))
    equity_curve.plot(marker='o', color='blue')
    plt.title("📈 Equity Curve Over Time")
    plt.xlabel("Date")
    plt.ylabel("Capital (INR)")
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.axhline(initial_capital, color='gray', linestyle='--', linewidth=1, label="Initial Capital")
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

    # Win rate
    calculate_win_rate(output_df)

    # Expected Payoff
    calculate_expected_payoff(output_df)

    # Max Drawdown
    calculate_max_drawdown(equity_curve.values)

    # Calculate CAGR
    cagr = calculate_cagr(initial_capital, final_capital, equity_curve)


   # Month-wise P&L
    month_pnl = plot_monthly_profit_loss(output_df)

   # Capture Metrics
    win_pct = calculate_win_rate(output_df)
    expected_payoff = calculate_expected_payoff(output_df)
    max_draw_amt, max_draw_pct = calculate_max_drawdown(equity_curve.values)

   # Save with timestamped filename
    export_backtest_summary_to_single_page_pdf(
      threshold_stats=threshold_stats,
      total_stocks=len(output_df),
      month_pnl=month_pnl,
      final_capital=final_capital,
      initial_capital=initial_capital,
      win_pct=win_pct,
      expected_payoff=expected_payoff,
      max_drawdown=(max_draw_amt, max_draw_pct),
      equity_curve=equity_curve,
      output_path=pdf_output_path,
      pdf_title=pdf_filename.replace('.pdf', '')  ,# remove extension
      cagr=cagr
    )



if __name__ == "__main__":
    main()

