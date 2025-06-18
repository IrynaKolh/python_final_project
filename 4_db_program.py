import sqlite3

def get_connection():
    """
    Establish and return a connection to the SQLite database.
    """
    try:
        return sqlite3.connect("baseball.db")
    except sqlite3.Error as e:
        print(f"Error connecting to DB: {e}")
        return None

def show_menu():
    """
    Display the command-line menu for the baseball analytics tool.
    """
    print("""
    ===!!! Baseball Analytics Menu !!!===
    1. Top 5 Batting Average by Year
    2. Most Productive Players (HR + RBI + Hits) for all history
    3. Average On-Base % per League
    4. Team Performance Comparison by Year
    5. High Slugging > 0.5 and OBP > 0.4 (with optional filters)
    0. Exit
    """)

def top_batting_average_by_year(conn, year):
    """
    Show top 5 players with the highest batting average in the specified year.
    """
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT Player, Team, batting_average
            FROM batting_average
            WHERE Year = ?
            ORDER BY batting_average DESC
            LIMIT 5
        """, (year,))
        rows = cursor.fetchall()
        print(f"\n Top 5 Batting Averages in {year}")
        for row in rows:
            print(row)
    except Exception as e:
        print("Error in query:", e)

def most_productive_players(conn):
    """
    List top 10 players with the highest sum of home runs, RBI, and hits (across all seasons).
    """
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT hr.Player, hr.Team, hr.home_runs, rbi.rbi, hits.hits
            FROM home_runs hr
            JOIN rbi ON hr.Year = rbi.Year AND hr.Player = rbi.Player
            JOIN hits ON hr.Year = hits.Year AND hr.Player = hits.Player         
            ORDER BY hr.home_runs + rbi.rbi + hits.hits DESC
            LIMIT 10
        """)
        rows = cursor.fetchall()
        print("\n Most Productive Players (HR + RBI + Hits):")
        for row in rows:
            print(row)
    except Exception as e:
        print("Error in query:", e)

def average_on_base_by_league(conn):
    """
    Show average On-Base Percentage (OBP) grouped by league.
    """
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT League, ROUND(AVG(on_base_percentage), 3) as avg_obp
            FROM on_base_percentage
            GROUP BY League
            ORDER BY avg_obp DESC
        """)
        rows = cursor.fetchall()
        print("\n Average OBP by League:")
        for row in rows:
            print(row)
    except Exception as e:
        print("Error:", e)

def team_performance_by_year(conn, year):
    """
    Compare teams' total performance metrics (runs, RBI, home runs) in the specified year.
    """
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT runs.Team,
                   SUM(runs.runs) as total_runs,
                   SUM(rbi.rbi) as total_rbi,
                   SUM(hr.home_runs) as total_home_runs
            FROM runs
            JOIN rbi ON runs.Year = rbi.Year AND runs.Player = rbi.Player
            JOIN home_runs hr ON runs.Year = hr.Year AND runs.Player = hr.Player
            WHERE runs.Year = ?
            GROUP BY runs.Team
            ORDER BY total_runs DESC
        """, (year,))
        rows = cursor.fetchall()
        print(f"\n🏟️ Team Performance in {year}")
        for row in rows:
            print(row)
    except Exception as e:
        print("Error:", e)

def high_slugging_and_onbase(conn, year=None, league=None, player=None):
    """
    Display players with slugging average > 0.5 and on-base percentage > 0.4.
    Optional filters: year, league, player name (partial match).
    """
    try:
        cursor = conn.cursor()
        query = """
            SELECT sa.Player, sa.Team, sa.slugging_average, obp.on_base_percentage, sa.Year, sa.League
            FROM slugging_average sa
            JOIN on_base_percentage obp
              ON sa.Year = obp.Year AND sa.Player = obp.Player
            WHERE sa.slugging_average > 0.5
              AND obp.on_base_percentage > 0.4
        """
        params = []

        if year:
            query += " AND sa.Year = ?"
            params.append(year)
        if league:
            query += " AND sa.League = ?"
            params.append(league.upper())
        if player:
            query += " AND sa.Player LIKE ?"
            params.append(f"%{player}%")

        query += " ORDER BY sa.slugging_average DESC"

        cursor.execute(query, params)
        rows = cursor.fetchall()

        if not rows:
            print("\n No players match the criteria.")
        else:
            print("\n Players with Slugging > 0.5 and OBP > 0.4:")
            for row in rows:
                print(f"Player: {row[0]}, Team: {row[1]}, Year: {row[4]}, League: {row[5]}, Slugging: {row[2]:.3f}, OBP: {row[3]:.3f}")
    except Exception as e:
        print("Error:", e)

def main():
    """
    Main driver function to display the menu and execute selected queries.
    """
    conn = get_connection()
    if not conn:
        return

    while True:
        show_menu()
        choice = input("Select an option: ").strip()

        if choice == "1":
            year = input("Enter year (e.g., 2005): ").strip()
            top_batting_average_by_year(conn, year)
        elif choice == "2":
            most_productive_players(conn)
        elif choice == "3":
            average_on_base_by_league(conn)
        elif choice == "4":
            year = input("Enter year (e.g., 2010): ").strip()
            team_performance_by_year(conn, year)
        elif choice == "5":
            year = input("Enter year (optional, press Enter to skip): ").strip() or None
            league = input("Enter league (AL or NL, optional): ").strip() or None
            player = input("Enter player name (partial or full, optional): ").strip() or None
            high_slugging_and_onbase(conn, year, league, player)
        elif choice == "0":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please enter a number from the menu.")

    conn.close()

if __name__ == "__main__":
    main()
