using System;
using System.IO;
using System.Text;
using RimWorld;
using Verse;

namespace RimMandrake.Inhabited
{
    /// <summary>
    /// Writes a report to DISK as well as to the log, and says where it went.
    ///
    /// 🔴 WHY THIS EXISTS, AND IT IS NOT TIDINESS. The architecture soak is
    /// `save -> quit to desktop -> reload -> compare`, and its whole value is the
    /// comparison against a baseline taken before the quit. **`Player.log` is
    /// ROTATED at every launch, not appended** — the launcher moves it to
    /// `Player-prev.log` and destroys the previous `Player-prev.log`. So a
    /// baseline that lives only in the log is gone at exactly the moment the
    /// second half of the test needs it, and the load that produced it has to be
    /// paid for again.
    ///
    /// This file is append-only and outside the game's own data, so it survives
    /// any number of launches.
    /// </summary>
    public static class InhabitedReport
    {
        private const string FolderName = "InhabitedReports";
        private const string FileName = "roster_reports.txt";

        /// <summary>The folder, created on first use. Beside Saves/ and Config/.</summary>
        public static string FolderPath
        {
            get
            {
                string dir = Path.Combine(GenFilePaths.SaveDataFolderPath, FolderName);
                if (!Directory.Exists(dir))
                {
                    Directory.CreateDirectory(dir);
                }
                return dir;
            }
        }

        public static string FilePath => Path.Combine(FolderPath, FileName);

        /// <summary>
        /// Append <paramref name="body"/> under a stamped heading, and log ONE
        /// line saying where it went. The log line is a pointer, not the report:
        /// the report is the thing that has to outlive the launch.
        /// </summary>
        public static void Write(string title, string body)
        {
            StringBuilder sb = new StringBuilder();
            sb.AppendLine();
            sb.AppendLine("=====================================================================");
            sb.AppendLine(title);
            sb.AppendLine("  real time : " + DateTime.Now.ToString("yyyy-MM-dd HH:mm:ss"));
            sb.AppendLine("  game tick : " + Find.TickManager.TicksGame
                          + "   day " + GenDate.DaysPassed);
            sb.AppendLine("=====================================================================");
            sb.AppendLine(body);

            string path = FilePath;
            try
            {
                File.AppendAllText(path, sb.ToString());
                Log.Message("[RimMandrake.Inhabited] " + title + " -> " + path);
            }
            catch (Exception e)
            {
                // Falling back to the log is better than losing the report, even
                // though the log will not survive the next launch.
                Log.Warning("[RimMandrake.Inhabited] could not write " + path + ": " + e.Message
                            + "\nReport follows, and it will NOT survive the next launch:\n"
                            + sb);
            }
        }
    }
}
